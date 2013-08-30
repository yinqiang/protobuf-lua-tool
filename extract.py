#!/usr/bin/env python
# -*- encoding:utf8 -*-

import sys, os, re

proto_head = "//package core.io.protocol;\n\n"
base_types = ["int32", "int64", "uint32", "uint64", "float", "double", "string", "bool", "enum"]

def depends(msg, rex, m):
	for r in rex.finditer(msg):
		if r:
			dep_type = r.group()[9:]
			if not dep_type in base_types:
				m[dep_type] = "import \"" + dep_type + ".proto\";"


def main(dir):
	re_message = re.compile("message\s\w+")
	re_end = re.compile("}")
	re_name = re.compile("\w+")
	re_dep_optional = re.compile("optional\s\w+")
	re_dep_repeated = re.compile("repeated\s\w+")

	for filename in os.listdir(dir):
		filetype = filename[-6:]
		if filetype == ".proto":
			f = open(dir + filename)
			buf = f.read()
			f.close()
			
			# scan 'message'
			start = []
			for r in re_message.finditer(buf):
				if r:
					start.append(r.start())
			
			# scan '}'
			end = []
			for r in re_end.finditer(buf):
				if r:
					end.append(r.end())
			
			# other message ware included in
			msgs = []
			# import other protocols
			imports = []
			selfname = filename[:-6]
			for i in range(0, len(start)):
				msg = buf[start[i]:end[i]]
				msg_name = re_name.search(msg[8:]).group()

				msgs.append(msg)

				# depends
				msg_dep = {}
				depends(msg, re_dep_optional, msg_dep)
				depends(msg, re_dep_repeated, msg_dep)
				
				buf_out = proto_head
				if len(msg_dep) > 0:
					buf_out += "\n".join(msg_dep.values()) + "\n\n"
				buf_out  += msg + "\n\n"

				# output other message files
				f = open(msg_name + ".proto", "w")
				f.write(buf_out)
				f.close()


if __name__ == "__main__":
	dir = sys.argv[1]
	main(dir)