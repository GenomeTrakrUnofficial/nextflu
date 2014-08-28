# create phylogeny from alignment
# raxml will complain about identical sequences, but still includes them all in the resulting tree
# writes out newick.tree file

import os, re, time, seqmagick
import dendropy
from io_util import *

OUTGROUP = 'A/Beijing/32/1992'

def to_json(node):
	json = {}
	if hasattr(node, 'clade'):
		json['clade'] = node.clade
	if node.taxon:
		json['strain'] = str(node.taxon).replace("'", '')
	if hasattr(node, 'layout'):
		json['layout'] = round(node.layout, 5)
	if hasattr(node, 'distance'):
		json['distance'] = round(node.distance, 5)	
	if hasattr(node, 'date'):
		json['date'] = node.date
	if hasattr(node, 'seq'):
		json['seq'] = node.seq
	if node.child_nodes():
		json["children"] = []
		for ch in node.child_nodes():
			json["children"].append(to_json(ch))
	return json
	
def get_layout(node):
	"""Return y location based on recursive mean of daughter locations"""	
	if hasattr(node, 'layout'):
		return node.layout	
	if node.child_nodes():
		mean = 0
		for ch in node.child_nodes():
			mean += get_layout(ch)
		return mean / float(len(node.child_nodes()))
		
def get_distance(node):
	"""Return x location based on total distance from root"""
	root = node.get_tree_root()
	return node.get_distance(root)

def reroot(tree):
	"""Reroot tree to outgroup"""
#	outgroup_node = tree.find_node_with_taxon_label(OUTGROUP)	
	outgroup = None
	for node in tree:
		if node.name == OUTGROUP:
			outgroup = node
			break
	if outgroup:
		tree.set_outgroup(outgroup)
		
def collapse(tree):
	"""Collapse short edges to polytomies"""
	for e in tree.postorder_edge_iter():
		if e.length < 0.00001 and e.is_internal():
			e.collapse()

def add_node_attributes(tree):
	"""Add clade, distance and layout attributes to all nodes in tree"""
	clade = 0
	layout = 0
	for node in tree.postorder_node_iter():
		node.clade = clade
		clade += 1
		if node.is_leaf():
			node.layout = layout
			layout += 1

	for node in tree.postorder_node_iter():
		node.layout = get_layout(node)
		node.distance = node.distance_from_root()

def add_virus_attributes(viruses, tree):
	"""Add date and seq attributes to all tips in tree"""
	strain_to_date = {}
	strain_to_seq = {}
	for v in viruses:
		strain_to_date[v['strain']] = v['date']
		strain_to_seq[v['strain']] = v['seq']
	for node in tree.postorder_node_iter():
		strain = str(node.taxon).replace("'", '')
		if strain_to_date.has_key(strain):
			node.date = strain_to_date[strain]
		if strain_to_seq.has_key(strain):
			node.seq = strain_to_seq[strain]

def cleanup():
	try:
		os.remove('temp.fasta')
	except OSError:
		pass
	try:
		os.remove('temp.phyx')
	except OSError:
		pass
	try:
		os.remove('temp.phyx.reduced')
	except OSError:
		pass		
	try:
		os.remove('RAxML_info.out')
	except OSError:
		pass	
	try:
		os.remove('RAxML_log.out')
	except OSError:
		pass		
	try:
		os.remove('RAxML_parsimonyTree.out')
	except OSError:
		pass
	try:
		os.remove('RAxML_result.out')
	except OSError:
		pass
									
def main():

	print "--- Tree at " + time.strftime("%H:%M:%S") + " ---"
	
	cleanup()	
	
	viruses = read_json('virus_clean.json')
	write_fasta(viruses, 'temp.fasta')
	os.system("seqmagick convert temp.fasta temp.phyx")
	os.system("raxml -T 6 -s temp.phyx -n out -c 25 -f d -m GTRCAT -p 344312987")
	os.rename('RAxML_bestTree.out', 'tree.newick')
	with open('tree.newick', 'r') as file:
		newick = file.read().replace('\n', '')	
		newick = re.sub(r'(A/[^\:]+)', r"'\1'", newick)
	with open('tree.newick', 'w') as file:
		file.write(newick)
		
	tree = dendropy.Tree.get_from_path("tree.newick", "newick")	
	tree.ladderize(ascending=False)
	collapse(tree)
	add_node_attributes(tree)
	add_virus_attributes(viruses, tree)

	write_json(to_json(tree.seed_node), "tree.json")

	cleanup()
	
if __name__ == "__main__":
    main()