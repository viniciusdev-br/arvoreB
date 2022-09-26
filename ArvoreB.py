class NodeB:
	def __init__(self, isLeaf = False):
		self.leaf = isLeaf # indica se é um nó folha
		self.keys = []
		self.child = []

class BTree:
	def __init__(self, order):
		self.root = NodeB(True)
		self.order = order 	#'order' é a ordem M da árovre

	def insert(self, valor):
		root = self.root
		if len(root.keys) == (2 * self.order) - 1:
			# Árvore atingiu o limite de chaves precisará usar o método split
			temp = NodeB()
			self.root = temp
			temp.child.insert(0, root)
			self.split_operation(temp, 0)
			self.only_insert(temp, valor)
		else:
			self.only_insert(root, valor)

	def only_insert(self, x, valor):
		i = len(x.keys) - 1
		if x.leaf:
			x.keys.append((None, None))
			while i >= 0 and valor[0] < x.keys[i][0]:
				x.keys[i + 1] = x.keys[i]
				i -= 1
			x.keys[i + 1] = valor
		else:
			while i >= 0 and valor[0] < x.keys[i][0]:
				i -= 1
			i += 1
			if len(x.child[i].keys) == (2 * self.order) - 1:
				self.split_operation(x, i)
				if valor[0] > x.keys[i][0]:
					i += 1
			self.only_insert(x.child[i], valor)

	def split_operation(self, x, i):
		# x é o pai do nó que será recortado
		#	i é o index do filho
		order = self.order
		y = x.child[i]
		z = NodeB(y.leaf)
		x.child.insert(i + 1, z)
		x.keys.insert(i, y.keys[order - 1])
    # Será z será preenchido pelas chaves de y de forma iterativa
		z.keys = y.keys[order : (2 * order) - 1]
		y.keys = y.keys[0 : order - 1]
		if not y.leaf:
			z.child = y.child[order : 2 * order]
			y.child = y.child[0 : order - 1]

	def delete(self, x, valor):
		order = self.order
		i = 0
		while i < len(x.keys) and valor[0] > x.keys[i][0]:
			i += 1
		if x.leaf: # Caso mais fácil, valor encontrado no nó filho, objetivo da recursão
			if i < len(x.keys) and x.keys[i][0] == valor[0]:
				x.keys.pop(i)
				return
			return
		if i < len(x.keys) and x.keys[i][0] == valor[0] : # valor encontrado no nó interno
			return self.delete_internal_node(x, valor, i)
		elif len(x.child[i].keys) >= order:
			self.delete(x.child[i], valor)			
		else:
			#iteração até atingir o valor
			if i != 0 and i+2 < len(x.child):
				if len(x.child[i-1].keys) >= order:
					self.delete_sibling(x, i, i-1)
				elif len(x.child[i+1].keys) >= order:
					self.delete_sibling(x, i, i+1)
				else:
					self.del_merge(x, i, i+1)
			elif i == 0: 
				if len(x.child[i+1].keys) >= order:
					self.delete_sibling(x, i, i+1)
				else:
					self.del_merge(x, i, i+1)
			elif i+1 == len(x.child):
				if len(x.child[i-1].keys) >= order:
					self.delete_sibling(x, i, i-1)
				else:
					self.del_merge(x, i, i-1)
			self.delete(x.child[i], valor)
	
	def delete_internal_node(self, x, valor, i):
		order = self.order
		if x.leaf:
			if x.keys[i][0] == valor[0]:
				x.keys.pop(i)
				return
			return
		if len(x.child[i].keys) >= order : # Substitui a chave por seu antecessor e excluindo o antecessor
			x.keys[i] = self.delete_predecessor(x.child[i])
			return
		elif len(x.child[i+1].keys) >= order: # Substitui a chave por seu sucessor e excluindo o sucessor
			x.keys[i] = self.delete_successor(x.child[i+1])
			return
		else: # realiza o merge
			self.del_merge(x, i, i+1)
			self.delete_internal_node(x.child[i], valor, self.order - 1)

	def delete_predecessor(self, x):
		if x.leaf:
			return x.pop()
		n = len(x.keys) - 1
		if len(x.child[n].keys) >= self.order:
			self.delete_sibling(x, n+1, n)
		else:
			self.del_merge(x, n, n+1)
		self.delete_predecessor(x.child[n])

	def delete_successor(self, x):
		if x.leaf:
			return x.keys.pop(0)
		if len(x.child[1].keys) >= self.order:
			self.delete_sibling(x, 0, 1)
		else:
			self.del_merge(x, 0, 1)
		self.delete_successor(x.child[0])

	def del_merge(self, x, i, j): # Realiza o merge entre x.child[i], x.child[j] and x.keys[i]
		cnode = x.child[i]
		if j > i:			
			rsnode = x.child[j]
			cnode.keys.append(x.keys[i])
			for valor in range(len(rsnode.keys)): # Atribuindo chaves do nó irmão direito ao nó filho
				cnode.keys.append(rsnode.keys[valor])
				if len(rsnode.child) > 0:
					cnode.child.append(rsnode.child[valor])
			if len(rsnode.child) > 0:
				cnode.child.append(rsnode.child.pop())
			new = cnode
			x.keys.pop(i)
			x.child.pop(j)
		else : # Realiza o merge entre x.child[i], x.child[j] and x.keys[i]
			lsnode = x.child[j]
			lsnode.keys.append(x.keys[j])
			for i in range(len(cnode.keys)):
				lsnode.keys.append(cnode.keys[i])
				if len(lsnode.child) > 0:
					lsnode.child.append(cnode.child[i])
			if len(lsnode.child) > 0:
				lsnode.child.append(cnode.child.pop())
			new = lsnode
			x.keys.pop(j)
			x.child.pop(i)
		if x == self.root and len(x.keys) == 0:
			self.root = new

	def delete_sibling(self, x, i, j):
		cnode = x.child[i]
		if i < j:
			rsnode = x.child[j]
			cnode.keys.append(x.keys[i])
			x.keys[i] = rsnode.keys[0]
			if len(rsnode.child)>0:
				cnode.child.append(rsnode.child[0])
				rsnode.child.pop(0)
			rsnode.keys.pop(0)
		else :
			lsnode = x.child[j]
			cnode.keys.insert(0,x.keys[i-1])
			x.keys[i-1] = lsnode.keys.pop()
			if len(lsnode.child)>0:
				cnode.child.insert(0,lsnode.child.pop())

	def print_tree(self, x, l = 0):
		print("Nível ", l, " ", len(x.keys), end = ":")
		for i in x.keys:
			print(i, end=" ")
		print()
		l += 1
		if len(x.child) > 0:
			for i in x.child:
				self.print_tree(i, l)
	

	def search(self, valor, x = None, l = 0):
		l += 1
		if x != None:
			i = 0
			while i < len(x.keys) and valor > x.keys[i][0]:
				i += 1
			if i < len(x.keys) and valor == x.keys[i][0]:
				return (x, i, l)
			elif x.leaf:
				return None
			else:
				return self.search(valor, x.child[i], l)
		else:
			return self.search(valor, self.root)

B = BTree(4) # Inicializando a árvore

for i in range(40): # Inserindo chave valor
	B.insert((i, 10*i))
 
B.print_tree(B.root) # Print da árvore
print("\n")

B.delete(B.root,(3,)) # Removendo o valor 3

if B.search(39) != None: # Realiza a busca pelo valor 39
	(x, i, l) = B.search(39)
	print("Elemento encontrado no índice: ", i)
	print("Elemento encontrado no nível: ", l - 1)
	print("Elemento encontrado no nó: ", x.keys)
else:
	print("Elemento não encontrado")
print("\n")

B.print_tree(B.root) # Print após a remoção
