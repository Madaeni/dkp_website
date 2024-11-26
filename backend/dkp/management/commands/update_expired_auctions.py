from django.core.management.base import BaseCommand
from django.db.models.functions import Now

from dkp.models import Auction


class Command(BaseCommand):
    help = 'Updates the status of expired auctions.'

    def handle(self, *args, **options):
        expired_auctions = Auction.objects.filter(
            is_active=Auction.Status.ACTIVE,
            close_date__lt=Now(),
        )
        expired_auctions.update(is_active=Auction.Status.CLOSED)
        self.stdout.write(
            f'Successfully updated {expired_auctions.count()} lot(s)'
        )
