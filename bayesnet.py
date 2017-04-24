import numpy as np
import pydot
import math
from random import randint, random
import time
import datetime

class BayesNet():
	
	"""Modelling Bayesian Network"""
	def __init__(self, num_nodes):
		self.num_nodes = num_nodes
		self.grph = np.zeros((num_nodes, num_nodes))
		self.num_edges = 0
		self.BIC = 0

	def addEdge(self, a, b):
		assert ((a >= 0 or a < self.num_nodes) or (b >= 0 or b < self.num_nodes)), 'Vertex index out of bounds!'
		self.grph[a][b] = 1
		if self.isCyclic() == True or a == b:
			self.grph[a][b] = 0
			# print 'Could not add edge because it\'s no longer a DAG.'
			return False
		self.num_edges += 1;
		return True

	def deleteEdge(self, a, b):
		assert ((a >= 0 or a < self.num_nodes) or (b >= 0 or b < self.num_nodes)), 'Vertex index out of bounds!'
		if self.grph[a][b] == 1:
			self.grph[a][b] = 0
			self.num_edges -= 1
			return True
		return False


	def reverseEdge(self, a, b):
		assert ((a >= 0 or a < self.num_nodes) or (b >= 0 or b < self.num_nodes)), 'Vertex index out of bounds!'
		if self.grph[a][b] == 1:
			self.deleteEdge(a,b)
			if self.addEdge(b,a) == False:
				self.addEdge(a,b)
				return False
			return True
		return False

			

	def isEdge(self, a, b):
		assert ((a >= 0 or a < self.num_nodes) or (b >= 0 or b < self.num_nodes)), 'Vertex index out of bounds!'
		if self.grph[a][b] == 1:
			return True
		return False


	def isCyclic(self):
		visited = [False for i in xrange(self.num_nodes)]
		recstack = [False for i in xrange(self.num_nodes)]

		def isCyclicUtil(v):
			if not visited[v]:
				visited[v] = True
				recstack[v] = True

				for i in xrange(self.num_nodes):
					if self.grph[v][i] == 1:
						if not visited[i] and isCyclicUtil(i):
							return True
						elif recstack[i]:
							return True

			recstack[v] = False
			return False

		return any(isCyclicUtil(v) for v in xrange(self.num_nodes))
		

	def showNet(self, fname = 'bn_'+'{:%Y-%m-%d_%H:%M:%S}'.format(datetime.datetime.now())+'.png'):
		graph = pydot.Dot(graph_type='digraph')
		
		for i in xrange(self.num_nodes):
			graph.add_node(pydot.Node(str(i+1)))

		for i in xrange(self.num_nodes):
			for j in xrange(self.num_nodes):
				if self.grph[i][j] == 1:
					edge = pydot.Edge(str(i+1), str(j+1))
					graph.add_edge(edge)

		graph.write_png(fname)
		print 'Graph saved as '+ fname
		time.sleep(2)


	# To infer from the dataset
	def infer(self, M):
		return randint(1,M)


	# Utility to convert a number to Base3 array
	def base3(self, n, l):
		s = ''
		while n:
			s += str(n%3)
			n /= 3
		s = s+('0'*(l-len(s)))
		s = s[::-1]
		return [int(s[i]) for i in xrange(len(s))]


	# Calculate log-likelihood from the dataset
	def calc_LHood(self, M):
		lhood = 0
		for i in xrange(self.num_nodes):
			num_par_i = self.grph[:,i].tolist().count(1)
			tau = 3**num_par_i
			sig = 0
			for j in xrange(tau):
				asg = self.base3(j,num_par_i)
				g = 0
				for k in xrange(3):
					g += (math.lgamma((tau/3.) + self.infer(M)) - math.lgamma(tau/3.))
				sig += (math.lgamma(tau) - math.lgamma(tau + self.infer(M)) + g)
			lhood += sig

		return lhood


	# Utility for getting independent parameters of BN
	def getFreeParams(self):
		cnt = 0
		for i in xrange(self.num_nodes):
			if (self.grph[:,i].tolist().count(1) == 0):
				cnt += 1

		return 3*cnt


	# Computing BIC score for a given Bayesian Network
	def getBIC(self, M):
		# Temp scoring. Need to change
		nodes = self.num_nodes
		prior = 2*self.num_edges/float(nodes*(nodes-1))
		lhood = self.calc_LHood(M) #random()
		self.BIC = lhood + math.log(prior) - math.log(M)*self.getFreeParams()/2.0
		return self.BIC



'''if __name__ == '__main__':
	
	bnet = BayesNet(3)
	bnet.addEdge(0,1)
	bnet.addEdge(1,2)
	bnet.addEdge(0,1)
	bnet.showNet('test.png')

	print bnet.getBIC(1000)'''
