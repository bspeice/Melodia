from django.db import models
import re, itertools

class IntegerListField(models.TextField):
	"""Store a list of integers in a database string.
	Format is: 
	[<int_1>, <int_2>, <int_3>, ... , <int_n>]"""

	description = "Field type for storing lists of integers."

	__metaclass__ = models.SubfieldBase

	def __init__(self, *args, **kwargs):
		super(IntegerListField, self).__init__(*args, **kwargs)


	#Convert database to python
	def to_python(self, value):
		if isinstance(value, list):
			return value

		#Process a database string
		
		#Validation first
		if len(value) <= 0:
			return []

		if value[0] != '[' or value[-1] != ']':
			raise ValidationError("Invalid input to parse a list of integers!")

		#Note that any non-digit string is a valid separator
		_csv_regex = "[0-9]"
		csv_regex  = re.compile(_csv_regex)

		#Synonymous to:
		#string_list = filter(None, csv_regex.findall(value))
		string_list  = itertools.ifilter(None, csv_regex.findall(value))
		value_list   = [int(i) for i in string_list]

		return value_list

	#Convert python to database
	def get_prep_value(self, value):
		if not isinstance(value, list):
			raise ValidationError("Invalid list given to put in database!")

		separator_string = ", "

		list_elements = separator_string.join(map(str, value))

		return "[" + list_elements + "]"
