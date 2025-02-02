"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'shark.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'shark.dashboard.CustomAppIndexDashboard'
"""

from admin_tools.dashboard import AppIndexDashboard, Dashboard, modules
from admin_tools.utils import get_admin_site_name
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from shark.billing.dashboard import (
    LooseItemsDashboardModule,
    UnpaidInvoicesDashboardModule,
)


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for shark.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)
        # append a link list module for "quick links"
        self.children.append(
            modules.LinkList(
                _("Quick links"),
                layout="inline",
                draggable=False,
                deletable=False,
                collapsible=False,
                children=[
                    [_("Return to site"), "/"],
                    [_("Change password"), reverse("%s:password_change" % site_name)],
                    [_("Log out"), reverse("%s:logout" % site_name)],
                ],
            )
        )

        self.children.append(UnpaidInvoicesDashboardModule())
        self.children.append(LooseItemsDashboardModule())

        # append an app list module for "Applications"
        self.children.append(
            modules.AppList(
                _("Applications"),
                exclude=("django.contrib.*",),
            )
        )

        # append an app list module for "Administration"
        self.children.append(
            modules.AppList(
                _("Administration"),
                models=("django.contrib.*",),
            )
        )

        # append a recent actions module
        self.children.append(modules.RecentActions(_("Recent Actions"), 5))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for shark.
    """

    # we disable title because its redundant with the model list module
    title = ""

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _("Recent Actions"), include_list=self.get_app_content_types(), limit=5
            ),
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
