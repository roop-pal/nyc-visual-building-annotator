# Input: Takes in the GML file 
# Output: A Dictionary indexed by Building Identification with attributes
#         X (min, max), Y (min, max), Z (min, max), BIN, DOITT_ID, SOURCE_ID
def parse(GML_file):
	fp = open(GML_file)
	buildings = dict()
	current = None
	for line in fp:
		if "bldg:Building" in line:
			raw_name = fp.readline()
			bldg_id = raw_name.split('>')[1].split('<')[0]
			buildings[bldg_id] = dict()
			buildings[bldg_id]["X"] = [float("inf"),-float("inf")]
			buildings[bldg_id]["Y"] = [float("inf"),-float("inf")]
			buildings[bldg_id]["Z"] = [float("inf"),-float("inf")]
			current = bldg_id
		if "/bldg:Building" in line:
			current = None
		if "BIN" in line:
			raw_value = fp.readline()
			bld_id = raw_value.split('>')[1].split('<')[0]
			buildings[current]['BIN'] = bld_id
		if "DOITT_ID" in line:
			raw_value = fp.readline()
			bld_id = raw_value.split('>')[1].split('<')[0]
			buildings[current]['DOITT_ID'] = bld_id
		if "SOURCE_ID" in line:
			raw_value = fp.readline()
			bld_id = raw_value.split('>')[1].split('<')[0]
			buildings[current]['SOURCE_ID'] = bld_id
		if "<gml:posList>" in line and "</gml:posList>" in line:
			points = line.split('>')[1].split('<')[0]
			points = points.split(' ')
			for p in range(len(points)//3):
				x = float(points[3*p])
				y = float(points[3*p+1])
				z = float(points[3*p+2])
				if x > buildings[bldg_id]["X"][1]:
					buildings[bldg_id]["X"][1] = x
				if x < buildings[bldg_id]["X"][0]:
					buildings[bldg_id]["X"][0] = x
				if y > buildings[bldg_id]["Y"][1]:
					buildings[bldg_id]["Y"][1] = y
				if y < buildings[bldg_id]["Y"][0]:
					buildings[bldg_id]["Y"][0] = y
				if z > buildings[bldg_id]["Z"][1]:
					buildings[bldg_id]["Z"][1] = z
				if z < buildings[bldg_id]["Z"][0]:
					buildings[bldg_id]["Z"][0] = z
	return buildings

if __name__ == '__main__':
	dictionary = parse('DA_WISE_GMLs/DA12_3D_Buildings_Merged.gml')

	# Input Format is Bldg_XXXXXXXXXXXXXXXXX
	while True:
		query = input("What would you like to lookup? ")
		print(dictionary[query])