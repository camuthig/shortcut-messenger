from django.db.models.base import Model
from django.http.response import HttpResponseRedirect
from django.views import generic
from django.views.generic.edit import ModelFormMixin


class HandleFormView(ModelFormMixin):
    """A view to validate input using a model form and handle it separately.

    The goal of this class is to remove the `save` functionality from the Form classes, keeping them as dump input validation.
    Instead, a `handle_form` function is defined that should implement the business logic using the data. This logic can be
    implemented directly in the view or possibly moved into a service layer or onto the model itself.

    This class helps capture two logical nuances from the ModelFormMixin
    1. It saves the results of the `handle_form` to `self.object`. The ModelFormMixin would usually use the results of
        `form.save()`.
    2. It renders the redirect response, usually performed by the `FormMixin`.
    """

    def handle_form(self, form) -> Model:
        raise NotImplementedError()

    def form_valid(self, form):
        self.object = self.handle_form(form)
        return HttpResponseRedirect(self.get_success_url())


class ListView(generic.ListView):
    pass


class DetailView(generic.DetailView):
    pass


class CreateView(HandleFormView, generic.CreateView):
    pass


class UpdateView(HandleFormView, generic.UpdateView):
    pass


class DeleteView(generic.DeleteView):
    pass
