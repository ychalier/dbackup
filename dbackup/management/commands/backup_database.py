import os
import datetime
import zipfile
import smtplib
import email
from django.core.management.base import BaseCommand
from django.conf import settings
from dbackup import models


class Command(BaseCommand):
    """Backup database"""
    help = "Backup database"

    def handle(self, *args, **kwargs):
        smtp_settings = models.SmtpSettings.load()
        if smtp_settings.host == "":
            return
        db_filename = settings.DATABASES["default"]["NAME"]
        now = datetime.datetime.now()
        zip_filename = "backup-piweb-%s.zip" % now.strftime("%Y-%m-%d-%H-%M-%S")
        zip_file = zipfile.ZipFile(
            zip_filename,
            mode="w",
            compression=zipfile.ZIP_BZIP2,
        )
        zip_file.write(db_filename, arcname="db.sqlite3")
        zip_file.close()
        msg = email.mime.multipart.MIMEMultipart()
        msg["Subject"] = "[PIWEB BACKUP] %s" % now.strftime("%d/%m/%Y %H:%M:%S")
        msg["From"] = smtp_settings.addr_from
        msg["To"] = smtp_settings.addr_to
        msg.attach(email.mime.text.MIMEText(
            "The attached file contains the backup of the Piweb database.",
            "plain"
        ))
        part = email.mime.base.MIMEBase("application", "octet-stream")
        with open(zip_filename, "rb") as file:
            part.set_payload(file.read())
        email.encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            "attachment; filename=\"%s\"" % zip_filename
        )
        msg.attach(part)
        server = smtplib.SMTP_SSL(
            smtp_settings.host,
            int(smtp_settings.port)
        )
        server.ehlo()
        server.login(
            smtp_settings.user,
            smtp_settings.password
        )
        server.sendmail(
            smtp_settings.addr_from,
            smtp_settings.addr_to,
            msg.as_string()
        )
        server.close()
        os.remove(zip_filename)
