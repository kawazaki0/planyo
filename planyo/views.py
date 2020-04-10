import logging

from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from planyo.services.update_prop import UpdateUserComment, PlanyoIntegrationException
from .forms import CsvForm

logger = logging.getLogger(__name__)


def update_user(request):
    # print("test")
    # import pdb; pdb.set_trace()
    if not request.user.is_authenticated:
        return redirect('/admin')
    if request.method == 'POST':
        form = CsvForm(request.POST)
        if form.is_valid():
            environment = form['environment'].data
            file = form['file'].data
            user_comment = UpdateUserComment(environment)
            try:
                result = user_comment.bulk_update(file)
            except PlanyoIntegrationException as e:
                logger.error(f'Error during integration: {str(e)}')
                return HttpResponse(f'Błąd integracji. {str(e)}')
            return HttpResponse('Wyniki:<br><br>{}<br><br><a href="/">Wróć</a>'.format("<br>".join(result)))

    else:
        form = CsvForm()

    return render(request, 'csv_import.html', {'form': form})
