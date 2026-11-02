import json, sys
nb = json.load(open(r'C:\Users\nayak\Desktop\Intership Projects\CAExploratory Data Analysis\superstore_eda.ipynb', encoding='utf-8'))
print('cells:', len(nb['cells']))
for i, c in enumerate(nb['cells']):
    src = ''.join(c['source'])
    print('--- cell', i, c['cell_type'], 'outputs:', len(c.get('outputs', [])))
    print(src[:700])