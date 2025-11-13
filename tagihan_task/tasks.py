from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task(name='tagihan_task.tasks.buat_tagihan_otomatis_task')
def buat_tagihan_otomatis_task():
    """
    Tugas Celery untuk memicu management command 'buat_tagihan_otomatis'.
    """
    logger.info("Starting scheduled billing task...")
    try:
        # call_command akan menjalankan management command
        call_command('buat_tagihan_otomatis')
        logger.info("Scheduled billing task finished successfully.")
    except Exception as e:
        logger.error(f"Scheduled billing task failed with error: {e}")