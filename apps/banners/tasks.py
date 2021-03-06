from datetime import datetime

from django.db import IntegrityError, models

from celery.decorators import task

from banners.models import BannerImage, BannerInstance


@task
def add_click(user_id, banner_id, banner_img_id):
    """Increment the click count for a banner."""
    now = datetime.now()

    # Ensure that the banner image exists
    if not BannerImage.objects.filter(pk=banner_img_id).exists():
        return

    try:
        instance, created = BannerInstance.objects.get_or_create(
            user_id=user_id,
            badge_id=banner_id,
            image_id=banner_img_id
        )
    except IntegrityError:
        # One of the IDs is wrong, causing a foreign key constraint to fail.
        # This isn't an app error, so we ignore this.
        return

    stats, created = instance.clickstats_set.get_or_create(month=now.month,
                                                           year=now.year)
    stats.clicks = models.F('clicks') + 1
    stats.save()

    instance.clicks = models.F('clicks') + 1
    instance.save()
