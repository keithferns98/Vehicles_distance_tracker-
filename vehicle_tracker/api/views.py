from django.shortcuts import render
from datetime import datetime
import json
from rest_framework.views import APIView,Response
from core.models import TripInfo,VehicleTrails
from django.http import HttpResponse
from api.serializer import VehicleTrailsSerializer,TripInfoSerializer
from haversine import haversine
import csv
# http://127.0.0.1:8000/download/csv/?high=1520887932&low=1520595273
class DownloadCsvVehicleTrails(APIView):
    def get(self,request,format=None):
        results={}
        high_ts=request.GET.get('high',None)
        low_ts= request.GET.get('low',None)
        dt_high=datetime.fromtimestamp(int(high_ts))#15205695273
        print(dt_high)
        dt_low=datetime.fromtimestamp(int(low_ts))#1520887932,1520690678
        print(dt_low)
        vh=VehicleTrails.objects.select_related('fk_asset').filter(tis__gte=dt_low,tis__lte=dt_high).order_by('tis')
        serializer=VehicleTrailsSerializer(vh,many=True)
        print(len(serializer.data))
        output_dict = json.loads(json.dumps(serializer.data))
        for idx,row in enumerate(output_dict):
            print(row)
            curr_rec=row['fk_asset']['trip_id']
            if results.get(curr_rec) is None:
                results[curr_rec]={'day':1,'Licenseplatenumber':'','Distance':'0 kms' ,'AverageSpeed':0,'TransporterName':'','NumberofSpeedViolations':0,'last_coords':None,'source_ts':0}
                # results[curr_rec]['counter']+=1
                results[curr_rec]['source_ts']=datetime.strptime(row['tis'].split('T')[0],'%Y-%m-%d')
                print(results[curr_rec]['source_ts'])
                results[curr_rec]['Licenseplatenumber']=row['lic_plate_no']
                if results[curr_rec]['last_coords']==None:
                    results[curr_rec]['last_coords']=[row['lat'],row['lon']]
                elif row.get('osf'):
                    results[curr_rec]['NumberofSpeedViolations']+=1
                results[curr_rec]['TransporterName']=row.get('fk_asset').get('t_name')
            else:
                curr_cords=[row['lat'],row['lon']]
                prev_cords=results[curr_rec]['last_coords']
                act_distance_driven=results[curr_rec]['Distance'].split(' ')[0]
                curr_cords,prev_cords=[float(i) for i in curr_cords],[float(j) for j in prev_cords]
                curr_total_driven=haversine(curr_cords,prev_cords,unit='km')+float(act_distance_driven)
                results[curr_rec]['last_coords']=curr_cords
                results[curr_rec]['Distance']=f'{"%.2f" % curr_total_driven} kms.'
                curr_ts=datetime.strptime(row['tis'].split('T')[0],'%Y-%m-%d')
                t_days=curr_ts-results[curr_rec]['source_ts']
                results[curr_rec]['day']= (t_days.days if t_days.days else results[curr_rec]['day'])
                if row.get('osf'):
                    results[curr_rec]['NumberofSpeedViolations']+=1
                    c_speed= row.get('spd')
                    avgspeed=results[curr_rec]['AverageSpeed']
                dist,t=float(results[curr_rec]['Distance'].split(' ')[0]),results[curr_rec]['day']*24
                results[curr_rec]['AverageSpeed']=round(dist/t,1)
        response = HttpResponse(content_type='text/csv',status=200)
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.DictWriter(response, fieldnames=['Trip_id', 'Day','LicenseplateNumber', 'Distance','AverageSpeed','TransporterName','NumberofSpeedViolations'])
        writer.writeheader()
        if len(results)>0:
            for curr_element in results:
                per_idx=results[curr_element]
                writer.writerow({'Trip_id': curr_element,'Day':per_idx['day'], 'LicenseplateNumber':per_idx['Licenseplatenumber'],'Distance':per_idx['Distance'] , 'AverageSpeed': per_idx['AverageSpeed'],\
                'TransporterName':per_idx['TransporterName'],'NumberofSpeedViolations': per_idx['NumberofSpeedViolations']})
            return response
        else:
            return Response({'status':f'No records from {dt_high}-{dt_low}'}) 

