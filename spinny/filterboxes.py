from .models import box
from django.db.models import Q
from .serializers import box_serializers


def filter_boxes(queries):
    boxes = box.objects.all()
    if queries.get('min_length') is not None:
        boxes = boxes.filter(length__gte=queries.get('min_length'))
    if queries.get('min_breadth') is not None:
        boxes = boxes.filter(breadth__gte=queries.get('min_breadth'))
    if queries.get('min_height') is not None:
        boxes = boxes.filter(height__gte=queries.get('min_height'))
    if queries.get('min_box_area') is not None:
        boxes = boxes.filter(area__gte=queries.get('min_box_area'))
    if queries.get('min_box_volume') is not None:
        boxes = boxes.filter(volume__gte=queries.get('min_box_volume'))
    if queries.get('max_length') is not None:
        boxes = boxes.filter(length__lte=queries.get('max_length'))
    if queries.get('max_breadth') is not None:
        boxes = boxes.filter(breadth__lte=queries.get('max_breadth'))
    if queries.get('max_height') is not None:
        boxes = boxes.filter(height__lte=queries.get('max_height'))
    if queries.get('max_box_area') is not None:
        boxes = boxes.filter(area__lte=queries.get('max_box_area'))
    if queries.get('max_box_volume') is not None:
        boxes = boxes.filter(volume__lte=queries.get('max_box_volume'))
    if queries.get('min_date') is not None:
        boxes = boxes.filter(created_on__gte=queries.get('min_date'))
    if queries.get('max_date') is not None:
        boxes = boxes.filter(created_on__lte=queries.get('max_date'))
    if queries.get('email') is not None:
        boxes = boxes.filter(creator=queries.get('email'))

    # max_length = queries.get('max_length')
    # max_breadth = queries.get('max_breadth')
    # max_height = queries.get('max_height')
    # max_box_area = queries.get('max_box_area')
    # max_box_volume = queries.get('max_box_volume')

    # boxes = box.objects.filter(length__lt=max_length, breadth__lt=max_breadth, height__lt=max_height, area__lt=max_box_area, volume__lt=max_box_volume,
    #                            length__gt=min_length, breadth__gt=min_breadth, height__gt=min_height, area__gt=min_box_area, volume__gt=min_box_volume)
    # serializer = box_serializers(boxes, many=True)
    # print(serializer.data)
    return boxes
