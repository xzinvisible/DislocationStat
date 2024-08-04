from ovito.io import import_file
from ovito.modifiers import DislocationAnalysisModifier
from collections import Counter
from time import time

import os
os.environ["OVITO_THREAD_COUNT"] = "1"

fileinput = 'test.xyz'
pipeline = import_file(fileinput)  
modifiers = DislocationAnalysisModifier()
modifiers.input_crystal_structure = DislocationAnalysisModifier.Lattice.FCC
pipeline.modifiers.append(modifiers)

def dislocation(frame):
    data = pipeline.compute(frame)
    step = frame * 100

    print("step %d" % step)

    Cother = 0
    Cperfect = 0
    Cshockley = 0
    Cstairrod = 0
    Chirth = 0
    Cfrank = 0
    
    for line in data.dislocations.lines:

        burgers_vector = []
        for i in [0,1,2]:
            match abs(line.true_burgers_vector[i]):
                case x if 0.166 < x < 0.168:
                    burgers_vector.append('1/6')
                case x if 0.333 < x < 0.334:
                    burgers_vector.append('1/3')
                case x if 0.499 < x < 0.501:
                    burgers_vector.append('1/2')
                case x if x < 0.0001:
                    burgers_vector.append('0')
                case _:
                    burgers_vector.append('other')

        vector_counter = Counter(burgers_vector)

        if vector_counter['1/2'] == 2 and vector_counter['0'] == 1:
            Cperfect += 1
        elif vector_counter['1/6'] == 2 and vector_counter['1/3'] == 1:
            Cshockley += 1
        elif vector_counter['1/6'] == 2 and vector_counter['0'] == 1:
            Cstairrod += 1
        elif vector_counter['1/3'] == 1 and vector_counter['0'] == 2:
            Chirth += 1
        elif vector_counter['1/3'] == 3:
            Cfrank += 1
        else:
            Cother += 1
    
    print("%d    %d    %d    %d    %d    %d\n" % (Cother, Cperfect, Cshockley, Cstairrod, Chirth, Cfrank))

    return [step, 
            data.attributes['DislocationAnalysis.length.1/2<110>'], data.attributes['DislocationAnalysis.length.1/6<112>'], data.attributes['DislocationAnalysis.length.1/6<110>'],
            data.attributes['DislocationAnalysis.length.1/3<100>'], data.attributes['DislocationAnalysis.length.1/3<111>'], data.attributes['DislocationAnalysis.length.other'],
            data.attributes['DislocationAnalysis.total_line_length'],
            Cperfect, Cshockley, Cstairrod, Chirth, Cfrank, Cother]


if __name__ == '__main__':

    t_start = time()

    import multiprocessing as mp
    mp.set_start_method('spawn')

    print(" step    other    perfect     shockley      stair-rod      hirth      frank\n")

    frame = range(pipeline.source.num_frames)

    with mp.Pool(24) as pool:
        distat = list(pool.map(dislocation,frame))

    t_end = time()


    with open('DislocationLength.txt','w') as fl:
        fl.write(f"Dislocationn length {fileinput}:\n")
        fl.write('step     Perfect  Shockley Stair-rod Hirth    Frank    Other    Total\n')
        for i in range(len(distat)):
            fl.write(f'{distat[i][0]:9d} {distat[i][1]:7g}   {distat[i][2]:7g}   {distat[i][3]:7g}   {distat[i][4]:7g}   {distat[i][5]:7g}   {distat[i][6]:7g}   {distat[i][7]:7g}\n')

    with open('DislocationCount.txt','w') as fc:
        fc.write(f"Dislocation count {fileinput}:\n")
        fc.write('step     Perfect  Shockley Stair-rod Hirth    Frank    Other\n')
        for i in range(len(distat)):
            fc.write(f'{distat[i][0]:9d} {distat[i][8]:9d} {distat[i][9]:9d} {distat[i][10]:9d} {distat[i][11]:9d} {distat[i][12]:9d} {distat[i][13]:9d}\n')

    print(f"Computation took {t_end - t_start} seconds")




