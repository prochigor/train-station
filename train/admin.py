from django.contrib import admin

from train.models import Station, Route, TrainType, Train, Journey, Crew, Ticket, Order


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    search_fields = ("source__name", "destination__name")
    list_filter = ("source", "destination")


@admin.register(TrainType)
class TrainTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_filter = ("train_type",)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    search_fields = (
        "route__source__name",
        "route__destination__name",
        "train__train_type__name"
    )
    list_filter = (
        "train__train_type",
        "departure_time",
        "arrival_time",
        "crew"
    )


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    search_fields = ("order",)
    list_filter = ("journey__route",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = ("user__email", "user__first_name", "user__last_name")
    list_filter = ("created_at", "user__email")


admin.site.register(Crew)
