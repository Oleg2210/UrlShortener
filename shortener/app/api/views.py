import logging
from copy import deepcopy
from django.http import Http404, HttpResponseRedirect
from django.conf import settings
from django.core.cache import cache
from django.core.paginator import Paginator
from django.contrib.sessions.models import Session
from django.views.decorators.http import require_http_methods
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import ShortenSerializer, ShortenedListSerializer
from .models import ShortenedUrl

logger = logging.getLogger('django')


@require_http_methods(['GET'])
def redirect(request, shortened_id):
    link = cache.get(shortened_id, None)
    if link is None:
        try:
            link = ShortenedUrl.objects.get(shortened_id=shortened_id).link
            cache.set(shortened_id, link, timeout=settings.CACHE_TTL)
        except ShortenedUrl.DoesNotExist:
            raise Http404

    return HttpResponseRedirect(link)


class CommonApiView(APIView):
    @staticmethod
    def create_session_if_not_exists(request):
        if not request.session.exists(request.session.session_key):
            request.session.create()
        request.session.set_expiry(settings.SESSION_TTL)

    @staticmethod
    def make_link(request, path):
        return f"{request.scheme }://{request.META['HTTP_HOST']}/{path}"

    @classmethod
    def format_validated_data(cls, request, validated_data):
        formatted_data = deepcopy(validated_data)
        del(formatted_data['session'])
        formatted_data['shortened_link'] = cls.make_link(request, formatted_data['shortened_id'])
        return formatted_data


class CreateView(CommonApiView):
    def post(self, request):
        logger.info(f'post data: {request.data}')
        self.create_session_if_not_exists(request)
        request.data['session'] = request.session.session_key

        serializer = ShortenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.validated_data)
            formatted_data = self.format_validated_data(request, serializer.validated_data)
            if cache.get(formatted_data['shortened_id'], False):
                cache.set(formatted_data['shortened_id'], formatted_data['link'], timeout=settings.CACHE_TTL)
            return Response(formatted_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def options(self, request):
        info = {
            'required fields': ['link'],
            'optional fields': ['shortened_id']
        }
        return Response(info)


class ListView(CommonApiView):
    def get(self, request, page):
        self.create_session_if_not_exists(request)
        session = Session.objects.get(pk=request.session.session_key)
        shortened_links = ShortenedUrl.objects.filter(session=session)
        page_info = self.get_page_info(request, page, shortened_links)
        return Response(page_info)

    def get_page_info(self, request, page, data):
        if page is None:
            page = 1

        paginator = Paginator(data, settings.LINKS_PER_PAGE)
        page_obj = paginator.get_page(page)

        serializer = ShortenedListSerializer(page_obj.object_list, many=True)
        formatted_links = []
        for obj in serializer.data:
            obj['shortened_link'] = self.make_link(request, obj['shortened_id'])
            formatted_links.append(obj)

        page_info = {
            'current page': page_obj.number,
            'number of pages': paginator.num_pages,
            'next page': self.make_link(request, page_obj.next_page_number()) if page_obj.has_next() else None,
            'previous page': self.make_link(request, page_obj.previous_page_number()) if page_obj.has_previous() else None,
            'links': formatted_links
        }
        return page_info


class AvailableLinksView(CommonApiView):
    def get(self, request):
        info = {
            'available links': {
                self.make_link(request, 'api/shorten'): 'create new shortened link',
                self.make_link(request, 'api/shortened_links'): 'list of your shortened links',
                self.make_link(request, '<shortened_id>'): 'redirect to full url'
            }

        }
        return Response(info)

# Create your views here.
