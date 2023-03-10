from django.contrib import admin
from .models import Question, Choice
from django import forms
from django.forms.models import BaseInlineFormSet

class AtLeastOneRequiredInlineFormSet(BaseInlineFormSet):

    def clean(self):
        """
        Check if at least one choice has been added
        """
        super(AtLeastOneRequiredInlineFormSet, self).clean()
        if any(self.errors):
            return
        if not any(cleaned_data and not cleaned_data.get('DELETE', False)
            for cleaned_data in self.cleaned_data):
            raise forms.ValidationError('At least one choice required.')

class ChoicesInline(admin.TabularInline):
    model = Choice
    formset= AtLeastOneRequiredInlineFormSet
    extra = 2
    exclude= ['votes']
    
class QuestionAdmin(admin.ModelAdmin):
    inlines = (ChoicesInline,)
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    ordering = ['pub_date']
    date_hierarchy = 'pub_date'
    list_filter = ['pub_date']
    search_fields = ['question_text']

    
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()        
        for instance in instances:
            instance.save() 

admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice)