from django.db import models

# Create your models here.
class SumDB(models.Model):
    # id = models.AutoField(primary_key=True)
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.CharField(max_length=100)
    sum_content = models.CharField(max_length=250)

class queryDB(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    doc_id = models.ForeignKey(SumDB, on_delete=models.CASCADE)
    doc_name = models.CharField(max_length=100)