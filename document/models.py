from django.db import models

# Create your models here.
class DocInfo(models.Model):
    # id = models.AutoField(primary_key=True)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=150, default='')

    def __str__(self):
        return self.name

class SumDoc(models.Model):
    doc_id = models.ForeignKey(DocInfo, on_delete=models.CASCADE)
    sum_content = models.CharField(max_length=250)

class Keyword(models.Model):
    doc_id = models.ForeignKey(DocInfo, on_delete=models.CASCADE)
    kwd = models.CharField(max_length=50, default="None")

# class queryDB(models.Model):
#     # id = models.CharField(max_length=50, primary_key=True)
#     doc_id = models.ForeignKey(SumDB, on_delete=models.CASCADE)
#     doc_name = models.CharField(max_length=100)