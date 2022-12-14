from socket import MSG_CTRUNC
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
import pandas as pd


def create_dataframe():
    '''
    creating the dataframes for currency convert mid currency df
    creating dataframe for currency actually values with df1 
    '''
    #Dataframe for df has started creating
    columns = ['AUD','CAD','CNY','CZK','DKK','EUR','GBP','JPY','NOK','NZD','USD']
    data = [
        ['1:1', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'D'],
        ['USD', '1:1', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'D'],
        ['USD', 'USD', '1:1', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'D'],
        ['USD', 'USD', 'USD', '1:1', 'EUR', 'Inv', 'USD', 'USD', 'EUR', 'USD', 'EUR'],
        ['USD', 'USD', 'USD', 'EUR', '1:1', 'Inv', 'USD', 'USD', 'EUR', 'USD', 'EUR'],
        ['USD', 'USD', 'USD', 'D' ,'D', '1:1', 'USD', 'USD', 'USD', 'USD', 'USD'],
        ['USD', 'USD', 'USD', 'USD', 'USD', 'USD', '1:1', 'USD', 'USD', 'USD', 'D'],
        ['USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', '1:1', 'USD', 'USD', 'Inv'],
        ['USD', 'USD', 'USD', 'EUR', 'EUR', 'Inv', 'USD', 'USD', '1:1', 'USD', 'EUR'],
        ['USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', 'USD', '1:1', 'D'],
        ['Inv', 'Inv', 'Inv', 'EUR', 'EUR', 'Inv', 'Inv', 'D',   'EUR', 'Inv', '1:1']
    ]
    dataframe_1 = pd.DataFrame(data,columns=columns,index=columns)
    #Dataframe for df has been created 
    
    #Dataframe for df1 has started creating
   
    data1=[
        ['AUD',0.8371, 'USD'],
        ['CAD',0.8711,'USD',],
        ['USD',6.1715, 'CNY'],
        ['EUR',1.2315, 'USD'],
        ['GBP',1.5683, 'USD'],
        ['NZD',0.7750, 'USD'],
        ['USD',119.95, 'JPY'],
        ['EUR',27.6028, 'CZK'],
        ['EUR',7.4405, 'DKK'],
        ['EUR',8.6651,'NOK']
    ]
    dataframe_2= pd.DataFrame(data=data1,columns=['cur_from','cur_val','cur_to'])
    #Dataframe for df1 has been created
    # converting the missing value conversion 
    for index,val in dataframe_2.iterrows():
        row = {'cur_from':val['cur_to'],'cur_val':(1/val['cur_val']),'cur_to':val['cur_from']}
        dataframe_2 = dataframe_2.append(row,ignore_index=True)
    return dataframe_1, dataframe_2

 
def main(dataframe_1,dataframe_2,convert_from,convert_val,convert_to):
    
    empty_list = []
    is_finished = True
    while is_finished:
        mid_value_df_1 = dataframe_1.loc[convert_from,convert_to]
        if mid_value_df_1 in ['1:1','D','Inv']:
            empty_list.append(convert_from)
            empty_list.append(mid_value_df_1)
            empty_list.append(convert_to)
            is_finished = False
        else:
            empty_list.append(convert_from)
            convert_from = mid_value_df_1
            if mid_value_df_1 == convert_to:
                empty_list.append(mid_value_df_1)
                is_finished = False
    # print(empty_list,"------------")
    i = 0
    error_flag = False
    final_val = 1
    msg = 'Convertion'
    while len(empty_list)>i:
        prev = empty_list[i]
        if i >= len(empty_list)-1:
            break
        next = empty_list[i+1]
        if next in ['1:1','D','Inv']:
            if next == '1:1':
                break
            elif next in ['D','Inv']:
                i = i+2
                next = empty_list[i]
                tmp_df = dataframe_2.query(f'cur_from=="{prev}" & cur_to=="{next}"')
                if tmp_df.empty:
                    error_flag = True
                    break
                else:
                    final_val = final_val * dataframe_2.query(f'cur_from=="{prev}" & cur_to=="{next}"').iloc[0].cur_val
        else:
            temp_df = dataframe_2.query(f'cur_from=="{prev}" & cur_to=="{next}"')
            if temp_df.empty:
                error_flag = True
                break
            else:
                final_val = final_val * dataframe_2.query(f'cur_from=="{prev}" & cur_to=="{next}"').iloc[0].cur_val
                prev=next
                i = i+1
    if error_flag:
        msg = "OOps We are unable to convert the given currency........"
        final_value = 0
    else:
        final_value = final_val * convert_val  
    return round(final_value,2), msg  

class FxCalculator(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'index.html'
    def __init__(self):
        self.dataframe_1, self.dataframe_2 = create_dataframe()

    def get(self,request):
        '''
        get all the necessary values with get into the webpage 
        like currency drop downs
        '''
        currency = ['AUD','CAD','CNY','CZK','DKK','EUR','GBP','JPY','NOK','NZD','USD']
        return Response({'currency':currency, "msg":"Success"})
    def post(self,request):
        '''
        do the actual calculation of fx calculator
        '''
        convert_from = request.POST.get('convert_from','')
        convert_to = request.POST.get('convert_to','')
        convert_val = float(request.POST.get('convert_from_val'))
        # print(self.dataframe_1, self.dataframe_2)
        result,msg = main(self.dataframe_1, self.dataframe_2,convert_from,convert_val,convert_to)
        return JsonResponse({'result':result if result else '' ,'msg':msg})
       