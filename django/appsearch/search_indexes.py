from haystack import indexes
from .models import ModelQuestionbank


class ModelQuestionbankIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True) #works
    content_auto = indexes.EdgeNgramField(use_template=True, template_name='/mypath/templates/search/indexes/appsearch/template.txt') 

    def get_model(self):
        return ModelQuestionbank

    def index_queryset(self, using=None):
        return ModelQuestionbank.objects.all()
