from django.shortcuts import render, redirect
from django.http import FileResponse
from django.conf import settings
from .forms import ScrapeForm
from .models import ScrapeRequest
from .utils import scrape_location, apply_custom_filter
import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def scrape_form(request):
    if request.method == 'POST':
        form = ScrapeForm(request.POST)
        if form.is_valid():
            country = form.cleaned_data['country']
            city = form.cleaned_data['city']
            category = form.cleaned_data['category']
            filter_column = form.cleaned_data['filter_column']
            filter_value = form.cleaned_data['filter_value']
            
            logger.debug(f"Starting scrape for {country}, {city}, {category}, filter: {filter_column}={filter_value}")
            filename = scrape_location(
                request.user, country, city, category, filter_column, filter_value
            )
            if filename:
                logger.info(f"Scrape successful, redirecting to preview: {filename}")
                return redirect('preview_csv', filename=filename)
            else:
                logger.error(f"No data found for {country}, {city}, {category}")
                form.add_error(None, "No data found for the given inputs.")
    else:
        form = ScrapeForm()
    
    return render(request, 'scraper/scrape_form.html', {'form': form})

def download_csv(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'csv_files', filename)
    logger.debug(f"Attempting to serve file: {filepath}")
    if os.path.exists(filepath):
        logger.info(f"Serving file: {filepath}")
        return FileResponse(open(filepath, 'rb'), as_attachment=True, filename=filename)
    else:
        logger.error(f"File not found: {filepath}")
        return render(request, 'scraper/error.html', {'message': f'File not found: {filename}'})

def view_downloads(request):
    scrape_requests = ScrapeRequest.objects.filter(user=request.user) if request.user.is_authenticated else ScrapeRequest.objects.filter(user__isnull=True)
    return render(request, 'scraper/view_downloads.html', {'scrape_requests': scrape_requests})

def preview_csv(request, filename):
    filepath = os.path.join(settings.MEDIA_ROOT, 'csv_files', filename)
    if not os.path.exists(filepath):
        logger.error(f"File not found for preview: {filepath}")
        return render(request, 'scraper/error.html', {'message': f'File not found: {filename}'})
    
    # Read CSV for preview
    try:
        df = pd.read_csv(filepath)
        # Ensure all rows are dictionaries
        data = df.to_dict('records')
        logger.debug(f"CSV data sample: {data[:2]}")
        # Verify each row is a dict
        for i, row in enumerate(data):
            if not isinstance(row, dict):
                logger.error(f"Row {i} is not a dictionary: {row}")
                data[i] = {}  # Replace with empty dict to avoid template errors
        columns = df.columns.tolist()
    except Exception as e:
        logger.error(f"Error reading CSV {filepath}: {e}")
        return render(request, 'scraper/error.html', {'message': f'Error reading CSV: {str(e)}'})
    
    return render(request, 'scraper/preview_csv.html', {
        'filename': filename,
        'data': data,
        'columns': columns,
        'scrape_request': ScrapeRequest.objects.filter(csv_file=f"csv_files/{filename}").first()
    })

def test_filter(request):
    return render(request, 'scraper/test_filter.html', {
        'test_dict': {'name': 'Test'}
    })