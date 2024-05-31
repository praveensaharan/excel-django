from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
from .forms import UploadFileForm


def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                else:
                    return HttpResponse("Invalid file format")

                # Rename columns to avoid spaces
                df.rename(columns={'Cust State': 'Cust_State',
                          'DPD': 'DPD', 'Cust Pin': 'Cust_Pin'}, inplace=True)

                # Process the DataFrame to get necessary insights
                state_counts = df['Cust_State'].value_counts(
                ).reset_index().to_dict(orient='records')

                top_pins = df['Cust_Pin'].value_counts().nlargest(
                    10).reset_index().to_dict(orient='records')
                dpd_summary = df['DPD'].describe().to_frame(
                ).reset_index().to_dict(orient='records')
                dpd_by_state = df.groupby('Cust_State')['DPD'].describe(
                ).reset_index().to_dict(orient='records')
                for item in dpd_by_state:
                    item['twenty_five_percent'] = item.pop('25%')
                    item['fifty_percent'] = item.pop('50%')
                    item['seventy_five_percent'] = item.pop('75%')

                date_summary = df.groupby('Date')['DPD'].describe(
                ).reset_index().to_dict(orient='records')
                for item in date_summary:
                    item['twenty_five_percent'] = item.pop('25%')
                    item['fifty_percent'] = item.pop('50%')
                    item['seventy_five_percent'] = item.pop('75%')
                state_date_counts = df.groupby(['Date', 'Cust_State']).size().unstack(
                    fill_value=0).reset_index().to_dict(orient='records')

                context = {
                    'state_counts': state_counts,
                    'top_pins': top_pins,
                    'dpd_summary': dpd_summary,
                    'dpd_by_state': dpd_by_state,
                    'date_summary': date_summary,
                    'state_date_counts': state_date_counts,
                }

                return render(request, 'myapp/summary.html', context)
            except Exception as e:
                return HttpResponse(f"Error processing file: {e}")
    else:
        form = UploadFileForm()
    return render(request, 'myapp/upload.html', {'form': form})
