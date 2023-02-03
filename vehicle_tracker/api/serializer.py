from rest_framework.serializers import ModelSerializer,CharField,RelatedField
from core.models import VehicleTrails,TripInfo


class TripInfoSerializer(ModelSerializer):
    class Meta:
        model=TripInfo
        fields="__all__"

class VehicleTrailsSerializer(ModelSerializer):
    fk_asset=TripInfoSerializer()
    class Meta:
        model=VehicleTrails
        fields='__all__'