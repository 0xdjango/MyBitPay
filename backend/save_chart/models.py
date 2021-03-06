from django.db import models


class Chart(models.Model):
	ownerSource = models.CharField(max_length=200, db_index=True)
	ownerId = models.CharField(max_length=200, db_index=True)
	name = models.CharField(max_length=200)
	symbol = models.CharField(max_length=50)
	resolution = models.CharField(max_length=10)
	lastModified = models.DateTimeField()
	content = models.JSONField()

	def __str__(self):
		return self.ownerSource + ":" + self.ownerId

	def setContent(self, _content):
		self.content = _content


class StudyTemplate(models.Model):
	ownerSource = models.CharField(max_length=200, db_index=True)
	ownerId = models.CharField(max_length=200, db_index=True)
	name = models.CharField(max_length=200)
	content = models.JSONField()

	def __str__(self):
		return self.ownerSource + ":" + self.ownerId

	def setContent(self, _content):
		self.content = _content

class DrawingTemplate(models.Model):
	ownerSource = models.CharField(max_length=200, db_index=True)
	ownerId = models.CharField(max_length=200, db_index=True)
	name = models.CharField(max_length=200)
	tool = models.CharField(max_length=200)
	content = models.JSONField(null=True)

	def __str__(self):
		return self.ownerSource + ":" + self.ownerId

	def setContent(self, _content):
		self.content = _content
