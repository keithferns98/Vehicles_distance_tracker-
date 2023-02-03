from django.db import models

# Create your models here.
from django.db import models

class TripInfo(models.Model):
    trip_id=models.IntegerField()
    t_name=models.CharField(max_length=255)
    quantity=models.IntegerField()
    vehicle_number=models.CharField(max_length=30)
    tc_datetime=models.DateTimeField()

    def __str__(self):
        return f'TripInfo:{self.trip_id}'

class VehicleTrails(models.Model):
    fk_asset =models.ForeignKey(TripInfo,on_delete=models.CASCADE,related_name='trips',)
    lic_plate_no=models.CharField(max_length=30)
    lat=models.DecimalField(max_digits=10,decimal_places=6)
    lon=models.DecimalField(max_digits=10,decimal_places=6)
    tis=models.DateTimeField()
    spd=models.IntegerField()
    harsh_acceleration=models.BooleanField()
    hbk=models.BooleanField()
    osf=models.BooleanField()
    
    def __str__(self):
        return f'{self.fk_asset_id,self.lic_plate_no} was ingested'
    
    