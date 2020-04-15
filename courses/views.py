from .serializers import CourseSerializer
from .models import Course, Quiz
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from django.http import Http404


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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
        # data = self.get_queryset().filter(title__icontains='bAsIc')[:2] ---> Gives you 2 records only.
        # data = self.get_queryset().filter(title__icontains='bAsIc').values('id', 'title')[:2] ---> Gives you two fields only and data comes back in form of a dictionary key/value
        # data = self.get_queryset().filter(title__icontains='bAsIc').values_list('id', 'title')[:2] ---> Gives you values in a form of tuples instead of dictionaries
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)
        """ Alt code syntax:
        data = Course.objects.filter(id=4)
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)
        """

    @action(methods=['get'], detail=False)
    def courses_by_teacher(self, request):  # , *args, **kwargs):
        data = self.get_queryset().filter(
            teacher__username='admin')  # kwargs['user_id']) .... # teacher__username -> we filtered based on related model attribute
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def exclude_subject(self, request):
        data = self.get_queryset().exclude(subject__in=['Python', 'Java', 'PHP'])  # similar to NOT IN
        serializer = self.get_serializer_class()(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def latest_course(self, request):
        data = self.get_queryset().order_by(
            'created_at').last()  # whatever date field you have where created means create_date. I know created is not in publishers but this example is taken from somehwere else to deliver the concept
        serializer = self.get_serializer_class()(data)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def course_dates(self, request):
        # for some reason, the line below doesn't work here. I wrote th code for my reference
        data = Course.objects.datetimes('created_at',
                                        'year')  # datetimes gives you all the dates that your courses were created at. You get year only. You can pass month, hours, etc. We used datetimes() method cause created_at is of type datetime
        # if created_at had date only datatype, call: Course.objects.dates('created_at', 'year')
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def top_3_recent_courses(self, request):
        # .order_by() can accept any field or multiple fields, and can ever traverse relationships. Super handy. If you order by multiple fields, the first takes precedence
        data = Course.objects.filter(published=False).order_by('-created_at')[:3]
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def update_published_and_display_all_courses(self, request):
        # update all courses published to True
        Course.objects.update(
            published=True)  # there is an implicit all() such as Course.objects.all().update(published=True)
        data = Course.objects.all()
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def delete_sql_courses_and_display_all_courses(self, request):
        Course.objects.filter(subject__icontains='sql').delete()
        data = Course.objects.all()
        serializer = CourseSerializer(data, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def create_single_course(self, request):
        teacher = get_user_model().objects.get(username='admin')
        course = Course.objects.create(teacher=teacher, subject='Python', title='Django Basics')
        serializer = CourseSerializer(course)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def create_multiple_courses(self, request):
        teacher = get_user_model().objects.get(username='admin')
        course = Course.objects.bulk_create([
            Course(teacher=teacher, subject='Python1', title='Django Basics'),
            Course(teacher=teacher, subject='Python2', title='Django Basics'),
            Course(teacher=teacher, subject='Python3', title='Django Basics'),
        ])
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def get_or_create_a_course(self, request):
        teacher = get_user_model().objects.get(username='admin')
        # get or create checks if a record exist using all of the attributes that we give it.
        # If it does exist, we get that record back. If it doesn't exist, it'll create the
        # record and gives it back to us and gives a boolean value whether or not the record
        # was created. get_or_create() is useful like when you are creating tags or categories and want
        # to only have one record for each tag.
        # get_or_create may not well with Serializers. Check this link:
        # https://stackoverflow.com/questions/25026034/django-rest-framework-modelserializer-get-or-create-functionality
        # I wrote the code below for our reference only so we know how to write get_or_create()
        # for some reason, the line below doesn't work here. I wrote th code for my reference
        course = Course.objects.get_or_create(teacher=teacher, subject='Python7', title='Django Basics2')
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    """
        Use F object you want to keep track of a counter that gets updated real-time i.e. assume you have a quiz models with 
        an attribute called times_taken of type integer. times_taken is just a counter that keeps track how many quizzes are taken
        so far. times_taken increments value by 1 i.e. =+1 every time a user finoshes a quiz. To update 
        times_taken, you can do:
        
        data = Quiz.objects.all().update(times_taken=+1)
        
        The problem is you don't know what's max times_taken at THE MOMENT you update! times_taken could have been
        updated just seconds ago. Ideally, you have to grab the most recent times_taken and increment by one. To solve this
        issue and make sure you always increment on the most recent times_taken without worrying what's the max
        times_taken at the particular second given that times_taken could be very dynamics especially if you've lots of
        people taking quizzes at the same time. The solution is to use F object.
        
        from django.db.models import F
        quiz = Quiz.objects.all().update(times_taken=F('times_taken')+1)
        quiz.times_taken # gives you count e.g. 3
        quiz.refresh_from_db() # referesh the DB and get recent count
        quiz.times_taken # gives you count e.g. 4
        
        Use F() object on sensitive data that has to be up to date and correct. F() is very handy
        for reducing the number of queries you have to do and avoiding race conditions in your code.
    """

    """
        * Multiple filters use AND conditon:
        Course.objects.filter(title__icontains='sql', description__icontains='hello', published=True)
        
        * Use Q objects for complex conditions mixtures of ORs and ANDs
        from django.db.models import Q
        models.Course.objects.filter(
            Q(title__icontains='whatever')|Q(description__icontains='whatever'),
            published=True
        ) 
        # in the above code, we saying find records where (title LIKE '%whatever%' OR desc LIKE '%whatever%') AND published=True
        # published=True has to come after Q objects. Q objects should come first because Q objects are args and published=True represents kwargs and args always come before kwargs.
        # the Q objects are non keyword arguments, they're args.
        
        # Q objects aren't something you'll use in every project. For example, for searching, it's often better to use a dedicated search engine,
        # like elastic search, than to try and build up a solution with Q objects and their friends.   
    """

    @action(methods=['get'], detail=False)
    def try_q_object(self, request):
        course = Course.objects.filter(
            Q(title__icontains='php') | Q(description__icontains='java'),
            published=False
        )
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_annotate(self, request):
        #### Warning this doesn't work cause it refers to text and quiz
        #### which don't exist in my sample project.
        #### Use annotation if you want to do a thing on each item in the query set.
        #### So if we're doing it on each individual item in the query set that's called
        #### an annotation. If we're doing it on the entire query set then that is an aggregate.

        # The code below simply tells us give us total number of quizzes per course given that
        # text is a model and quiz is another model. Its like saying give total number of replies
        # per each post.
        # from django.db.models import Count
        course = Course.objects.filter(
            published=False
        ).annotate(total_reviews=Count('text', distinct=True) + Count('quiz', distinct=True))
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_aggregate(self, request):
        #### If we're doing it on the entire query set then that is an aggregate.

        # Gives you the total price of all php courses. Hence we don't have price field. Just assume we did.
        # from django.db.models import Sum
        course = Course.objects.filter(
            title__icontains='php'
        ).aggregate(total=Sum('price'))
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_aggregate_and_annotate(self, request):
        #### If we're doing it on the entire query set then that is an aggregate.
        course = Course.objects.filter(
            published=False
        ).annotate(total_reviews=Count('text', distinct=True) + Count('quiz', distinct=True))
        # You have to find a way to pass total through serializer or merge it with course somehow
        total = course.aggregate(total=Sum(
            'total_steps'))  # Gives you total quizzes of ALL courses. Its like getting total replies of ALL POSTS
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_prefetch_related(self, request):
        try:
            """
            Prefetch related goes off and fetches and Everything in the quiz is set and everything in the text is set..
            It is for getting alot of items. Use prefetch_related if you want to use reverse relationship like quiz to question
            
            So basically, the code below generates three different queries:
                SELECT * FROM courses_course WHERE published=True AND courses_course.id=1;
                SELECT * FROM courses_quiz WHERE courses_quiz.course_id=1;
                SELECT * FROM courses_text WHERE courses_text.course_id=1;
                
                Django assigns quiz and text to our course query set items.
                select_related seems better cause it returns one joined query
            """
            course = Course.objects.prefetch_related(
                'quiz_set', 'text_set'
            ).get(pk=1, published=True)
        except Course.DoesNotExist:
            raise Http404  # from django.http import Http404
        # You have to find a way to pass total through serializer or merge it with course somehow
        total = course.aggregate(total=Sum('total_steps'))
        serializer = CourseSerializer(course, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_select_related(self, request):
        try:
            """
                select_related is used on the model when you have the ForeignKey field. It is used to get small
                amount of items usually one item.
                 
                The codes below generates:
                
                SELECT * FROM courses_quiz INNER JOIN courses_course ON courses_quiz.course_id =
                courses_course.id WHERE courses.course.plublished = True AND courses_quiz.course_id=1

                
            """
            myquiz = Quiz.objects.select_related(
                'course'
            ).get(
                course_id=1, # I just added hardcoded value 1 to avoid red underlines. Instead, USE this: course_pk,
                pk=0, # I just added hardcoded value 1 to avoid red underlines. Instead, myquiz_pk,
                course__published=True
            )
        except Quiz.DoesNotExist:
            raise Http404  # from django.http import Http404
        serializer = CourseSerializer(myquiz, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def try_select_related_with_prefetch_related(self, request):
        try:
            """
                The codes below generates:
                
                SELECT * FROM courses_quiz INNER JOIN courses_course ON courses_quiz.course_id =
                courses_course.id WHERE courses.course.plublished = True AND courses_quiz.course_id=1
                AND courses_quiz.id=2
                
                SELECT * FROM courses_question WHERE courses_question.quiz_id = 2
                
                SELECT * FROM courses_answer WHERE courses_answer.question=2
            """
            myquiz = Quiz.objects.select_related(
                'course'
            ).prefetch_related(
                'question_set',
                'question_set__answer_set',
            ).get(
                course_id=1, # I just added hardcoded value 1 to avoid red underlines. Instead, USE this: course_pk,
                pk=1, # I just added hardcoded value 1 to avoid red underlines. Instead, myquiz_pk,
                course__published=True
            )
        except Quiz.DoesNotExist:
            raise Http404  # from django.http import Http404
        serializer = CourseSerializer(myquiz, many=True)
        return Response(serializer.data)