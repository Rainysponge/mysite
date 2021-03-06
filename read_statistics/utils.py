import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)
    if not request.COOKIES.get(key):
        # 总阅读数
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        # 战术加一
        readnum.read_num = readnum.read_num + 1
        readnum.save()
        # 当天阅读数
        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)

        readDetail.read_num += 1
        readDetail.save()

    return key  # cookies


def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    read_num = []
    dates = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))  # 聚类求和,read_num_sum得到求和值
        read_num.append(result['read_num_sum'] or 0)
    return dates, read_num
