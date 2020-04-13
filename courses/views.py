from .serializers import CourseSerializer
from .models import Course
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    ##################### START - FILTER METHODS ######################
    """
    The conditions are called field lookups and there are a lot of them. The ones I seem to 
    use the most often are gte (greater than or equal to), lte (less than or equal to), in (uh, just like Python's in keyword), 
    and icontains (case-insensitive in for strings). I'm sure you'll find some that you love, too.
    
    If C has a foreign key to B and B has a foreign key to A, you could
    do: C.objects.filter(b__a__id__in=[1, 5, 10]) to get all of the C objects
    that have a B object with an A object whose id attribute is 1, 5, or 10. Yes,
    this is an over-engineered, overly-complicated scenario, but you'll be surprised
    how often similar things come up.
    """

    @action(methods=['get'], detail=False)
    def search_by_title(self, request):
        data = self.get_queryset().filter(title__icontains='bAsIc')
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)
        """ Alt:
        data = Course.objects.filter(id=4)
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)
        """

    @action(methods=['get'], detail=False)
    def courses_by_teacher(self, request): #, *args, **kwargs):
        data = self.get_queryset().filter(teacher__username='admin')#kwargs['user_id']) .... # teacher__username -> we filtered based on related model attribute
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def exclude_subject(self, request):
        data = self.get_queryset().exclude(subject__in=['Python', 'Java', 'PHP']) # similar to NOT IN
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def latest_course(self, request):
        data = self.get_queryset().order_by('created_at').last()  # whatever date field you have where created means create_date. I know created is not in publishers but this example is taken from somehwere else to deliver the concept
        serializer = self.get_serializer_class()(data)
        return Response(serializer.data)

    ######################## END - FILTER METHODS #########################

    ##################### UPDATE AND DELETE ####################
    @action(methods=['get'], detail=False)
    def update_published_and_display_all_courses(self, request):
        # update all courses published to True
        Course.objects.update(published=True) # there is an implicit all() such as Course.objects.all().update(published=True)
        data = Course.objects.all()
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def delete_sql_courses_and_display_all_courses(self, request):
        Course.objects.filter(subject__icontains='sql').delete()
        data = Course.objects.all()
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

