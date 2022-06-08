from django_filters import rest_framework as filters

from reviews.models import Title


class CharFilterInFilter(filters.CharFilter, filters.BaseInFilter):
    pass


class TitleFilter(filters.FilterSet):
    genre = CharFilterInFilter(field_name="genre__slug", lookup_expr='in')
    category = CharFilterInFilter(
        field_name="category__slug", lookup_expr='in'
    )
    year = filters.CharFilter(field_name="year", lookup_expr='icontains')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ['genre', 'name', 'category', 'year']
