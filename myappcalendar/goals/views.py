from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import permissions
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from filters import GoalDateFilter, GoalCommentFilter
from goals.models import GoalCategory, Goal, Status, GoalComment
from goals.serializers import GoalCatCreateSerializer, GoalCategorySerializer, GoalCreateSerializer, GoalListSerializer, \
    GoalCommentCreateSerializer, GoalCommentListSerializer


class GoalCategoryCreateView(CreateAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCatCreateSerializer

    # def create(self, request, *args, **kwargs):
    #     request.data['user'] = request.user.id
    #     return super().create(request, *args, **kwargs)


class GoalCategoryListView(ListAPIView):
    model = GoalCategory
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCategorySerializer

    pagination_class = LimitOffsetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    ordering_fields = ["title", "created"]
    ordering = ["title"]
    # search_fields = ["=title"]
    filterset_fields = ['title']

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return GoalCategory.objects.filter(
            user=self.request.user, is_deleted=False
        )


class GoalCategoryView(RetrieveUpdateDestroyAPIView):
    model = GoalCategory
    serializer_class = GoalCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return GoalCategory.objects.filter(user=self.request.user, is_deleted=False)

    # Для того, чтобы категория не удалялась, при вызове delete, категория удаленные
    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        return instance


class GoalCreateView(CreateAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCreateSerializer


class GoalListView(ListAPIView):
    model = Goal
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalListSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalDateFilter
    pagination_class = LimitOffsetPagination
    ordering_fields = ["title", "created"]

    ordering = ["created"]

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return Goal.objects.filter(
            user=self.request.user
        )


class GoalView(RetrieveUpdateDestroyAPIView):
    model = Goal
    serializer_class = GoalListSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return Goal.objects.filter(
            user=self.request.user
        )

    # Добавляем в архив
    def perform_destroy(self, instance):
        instance.status = Status.archived
        instance.save()
        return instance


class GoalCommentCreateView(CreateAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentCreateSerializer


class GoalCommentListView(ListAPIView):
    model = GoalComment
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GoalCommentListSerializer

    #
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_class = GoalCommentFilter
    # search_fields = ["=goal__id"]
    filterset_fields = ['goal']
    # С этим дерьмом не работает.&search=%5Bobject%20Object%5D& search_fields
    pagination_class = LimitOffsetPagination
    ordering_fields = ["created"]
    ordering = ["-created"]

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return GoalComment.objects.filter(
            Q(user=self.request.user)
        )
    # Второй вариант если бы пользователя не было б в комментариях
    # def get_queryset(self):
    #     return GoalComment.objects.filter(
    #         Q(goal__user=self.request.user)
    #     )


class GoalCommentView(RetrieveUpdateDestroyAPIView):
    model = GoalComment
    serializer_class = GoalCommentListSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Фильтруем на текущего пользователя
    def get_queryset(self):
        return GoalComment.objects.filter(
            user=self.request.user
        )