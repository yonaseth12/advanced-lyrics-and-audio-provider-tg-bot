def parser_4096(long_string):
	temp_string=long_string
	list_to_return=[]
	while temp_string:
		if len(temp_string) <= 4096:
			list_to_return.append(temp_string)
			return list_to_return
		list_to_return.append(temp_string[:4096])
		temp_string=temp_string[4096:]