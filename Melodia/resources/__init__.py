import os, sys
def get_resource_dir():
	return os.path.dirname(
			os.path.abspath(__file__)
			)

def add_resource_dir():
	sys.path.append(get_resource_dir())
