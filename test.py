my_dict = dict()
keys_view = my_dict.keys()
keys_list = list(keys_view)
if len(keys_list) == 0:
    print("yes")
print(keys_list[0])  # 输出: ['a', 'b', 'c']