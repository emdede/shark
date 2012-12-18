# -*- coding: UTF-8 -*-

from decimal import Decimal
from datetime import datetime, date, timedelta

from django.conf import settings
from django.db import models
from django.db.models import signals
from django.utils.formats import date_format
from django.utils.translation import ugettext_lazy as _

from shark.utils.id_generators import IdField, DaysSinceEpoch
from shark.utils.rounding import round_to_centi

INVOICE_PAYMENT_TIMEFRAME = settings.SHARK.get('INVOICE_PAYMENT_TIMEFRAME', 14)
VAT_RATE_CHOICES = settings.SHARK.get('VAT_RATE_CHOICES', (Decimal(0), '0%'))
CUSTOMER_MODEL = settings.SHARK.get('CUSTOMER_MODEL', 'customer.Customer')


class Invoice(models.Model):
    #
    # general
    #
    customer = models.ForeignKey(CUSTOMER_MODEL,
            verbose_name=_('Customer'))
    # XXX replace this field by an IdField
    number = IdField(DaysSinceEpoch())

    #
    # address
    #
    address = models.TextField()

    net = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=_('net'))
    gross = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=_('gross'))

    #
    # status
    #
    created = models.DateField(
            default=date.today,
            verbose_name=_('Created'))
    reminded = models.DateField(blank=True, null=True,
            verbose_name=_('Reminded'))
    paid = models.DateField(blank=True, null=True,
            verbose_name=_('Paid'))

    class Meta:
        db_table = 'billing_invoice'
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')
        unique_together = (('customer', 'number'),)
        ordering = ('-created',)

    def __unicode__(self):
        return u'%s %s' % (_('Invoice'), self.number)

    def is_okay(self):
        if self.paid:
            return True
        if self.reminded is None:
            deadline = self.created + INVOICE_PAYMENT_TIMEFRAME
        else:
            deadline = self.reminded + INVOICE_PAYMENT_TIMEFRAME
        return date.today() <= deadline
    is_okay.short_description = _('Okay')
    is_okay.boolean = True

    @property
    def items(self):
        if not hasattr(self, '_item_cache'):
            self._item_cache = self.item_set.all()
        return self._item_cache

    def recalculate(self):
        self.net = sum(item.total for item in self.items)
        vat_amount = sum(vat_amount for vat_rate, vat_amount in self.vat)
        self.gross = self.net + vat_amount

    @property
    def vat(self):
        '''
        Return a list of (vat_rate, amount) tuples.
        '''
        # create a dict which maps the vat rate to a list of items
        vat_dict = {}
        for item in self.items:
            if item.vat_rate == 0:
                continue
            vat_dict.setdefault(item.vat_rate, []).append(item)
        # sum up item per vat rate and create an ordered list of
        # (vat_rate, vat_amount) tuples.
        vat_list = []
        for vat_rate, items in vat_dict.iteritems():
            amount = sum(item.total for item in items)
            vat_amount = round_to_centi(vat_rate * amount)
            vat_list.append((vat_rate, vat_amount))
        vat_list.sort()
        return vat_list


UNIT_CHOICES = (
    ('month', _('month')),
    ('year', _('year')),
)


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='item_set',
            blank=True, null=True,
            verbose_name=_('invoice'))
    customer = models.ForeignKey(CUSTOMER_MODEL,
            verbose_name=_('customer'))
    position = models.PositiveIntegerField(blank=True, null=True,
            verbose_name=_('position'))
    quantity = models.DecimalField(max_digits=10, decimal_places=2,
            default=Decimal('1'),
            verbose_name=_('quantity'))
    sku = models.CharField(max_length=20, blank=True,
            verbose_name=_('SKU'),
            help_text=_('Stock-keeping unit (e.g. Article number)'))
    text = models.CharField(max_length=200,
            verbose_name=_('description'))
    begin = models.DateField(default=date.today,
            verbose_name=_('begin'))
    end = models.DateField(blank=True, null=True,
            verbose_name=_('end'))
    price = models.DecimalField(max_digits=10, decimal_places=2,
            verbose_name=_('price'))
    unit = models.CharField(max_length=10, blank=True,
            choices=UNIT_CHOICES,
            verbose_name=_('unit'))
    discount = models.DecimalField(max_digits=3, decimal_places=2,
            default=Decimal('0.00'),
            verbose_name=('discount'))
    vat_rate = models.DecimalField(max_digits=3, decimal_places=2,
            choices=VAT_RATE_CHOICES,
            verbose_name=('VAT rate'))

    class Meta:
        db_table = 'billing_invoice_item'
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        unique_together = (('invoice', 'position'),)
        ordering = ('position',)

    def __unicode__(self):
        return u'#%d %s' % (self.position or 0, self.text)

    def save(self):
        if self.customer is None:
            if self.invoice is None:
                self.customer = self.invoice.customer
            else:
                raise RuntimeError('The customer must be set if no invoice is given')
        super(InvoiceItem, self).save()

    def get_period(self):
        begin = date_format(self.begin, 'SHORT_DATE_FORMAT')
        end = date_format(self.end, 'SHORT_DATE_FORMAT') \
                if self.end is not None \
                else _('one-time')
        return u'%s – %s' % (begin, end)
    get_period.short_description = _('Billing period')
    period = property(get_period)

    def get_subtotal(self):
        return round_to_centi(self.quantity * self.price)
    get_subtotal.short_description = _('Subtotal')
    subtotal = property(get_subtotal)

    @property
    def discount_percentage(self):
        return self.discount * 100

    @property
    def discount_amount(self):
        return round_to_centi(self.discount * self.subtotal)

    def get_total(self):
        return self.subtotal - self.discount_amount
    get_total.short_description = _('Sum of line')
    total = property(get_total)