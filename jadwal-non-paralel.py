import math
import random
from time import perf_counter
from datetime import datetime, timedelta
import psutil
from colorama import Fore, Style
from dbConfig import GetAllDB, GenerateData

# Initialize data from database
dataKuliah = GetAllDB('kuliah_teknik')
dataWaktu = GetAllDB('waktu2')
dataRuangan = GetAllDB('ruangan')
dataPreferensiDosen = GetAllDB('preferensi_waktu_dosen')

kuliah = GenerateData(dataKuliah)
waktu = GenerateData(dataWaktu)
ruangan = GenerateData(dataRuangan)
preferensi_dosen = {item['dosen']: {'preferensi_waktu': item['preferensi_waktu'], 'tidak_bisa_waktu': item['tidak_bisa_waktu']} for item in dataPreferensiDosen}

# Parameters
jml_kromosom = 4
per_sks = 50  # 1 sks = 50 menit
success = False
fitness = [None] * jml_kromosom
total_fitness = 0
cromosom_probability = []
randomValue = []
parent = []
best_fitness = 0
probability = []
crommosom = [None] * jml_kromosom
generataion = 0
max_generataion = 10
timeClash = {}
objectFitnes = {}
best_cromosom = []
crossover_rate = 75
mutation_rate = 25

def get_ram_usage():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available)

def returnIndexList(lst):
    return random.choice(range(len(lst)))

def arraySum(arr):
    return sum(arr)

def unique(lst):
    return list(set(lst))

def getRandom():
    global randomValue
    randomValue = [random.random() for _ in range(len(fitness))]
    print("\n3. Nilai Acak (0-1)")
    for i, value in enumerate(randomValue):
        print(f"Random[{i}] = {value}")

def getTotalFitness():
    global total_fitness
    total_fitness = sum(val['nilai'] for val in fitness)

def showCromosom(_cromosom):
    print("\nProses(1) Generate Cromosom ")
    for i, crom in enumerate(_cromosom):
        print(f"cromosom[{i}] {crom[0]}")

def showFitness():
    print("\nProses(2) Menghitung Fungsi Fitness ")
    for i, value in enumerate(fitness):
        print(f"f[{i}] {value['rumus']} = {value['nilai']}")
    getTotalFitness()
    print(f"Total Fitness = {total_fitness}")

def stringToSecond(time_string):
    hours, minutes = map(int, time_string.split(":"))
    return timedelta(hours=hours, minutes=minutes).total_seconds()

def get_rand_crommosom(_kuliah, _waktu, _ruangan):
    return {
        index: {
            'kuliah': index,
            'ruang': random.randint(0, len(_ruangan)-1),
            'waktu': random.randint(0, len(_waktu)-1)
        } for index in range(len(_kuliah))
    }

def isCheckTimeClash(gen1, gen2):
    clash1 = f"{gen1['waktu']}_{gen1['kuliah']}"
    clash2 = f"{gen2['waktu']}_{gen2['kuliah']}"

    if clash1 not in timeClash:
        waktu1 = waktu[gen1['waktu']]
        waktu2 = waktu[gen2['waktu']]
        bentrok = 0

        if gen1['waktu'] == gen2['waktu']:
            bentrok = 1
        elif waktu1[1] == waktu2[1]:
            sks1 = int(kuliah[gen1['kuliah']]['sks'])
            sks2 = int(kuliah[gen2['kuliah']]['sks'])
            awalJadwal1 = stringToSecond(waktu1[2])
            akhirJadwal1 = awalJadwal1 + sks1 * per_sks * 60
            awalJadwal2 = stringToSecond(waktu2[2])
            akhirJadwal2 = awalJadwal2 + sks2 * per_sks * 60
            if (
                awalJadwal1 == awalJadwal2 or
                awalJadwal1 > awalJadwal2 < akhirJadwal2 or
                akhirJadwal1 > awalJadwal2 < akhirJadwal2 or
                awalJadwal2 > awalJadwal1 < akhirJadwal1 or
                akhirJadwal2 > awalJadwal1 < akhirJadwal1
            ):
                bentrok = 1

        timeClash[clash1] = {clash2: bentrok}
        timeClash[clash2] = {clash1: bentrok}

    return timeClash[clash1][clash2]

def checkPreferensiDosen(dosen, waktu):
    if dosen in preferensi_dosen:
        return waktu in preferensi_dosen[dosen]['preferensi_waktu']
    return False

def checkTidakBisaWaktuDosen(dosen, waktu):
    if dosen in preferensi_dosen:
        return waktu in preferensi_dosen[dosen]['tidak_bisa_waktu']
    return False

def calculate_fitness(cro):
    global objectFitnes, success, best_cromosom, best_fitness, fitness

    cd_clashes = checkClashDosen(crommosom[cro])
    cr_clashes = checkClashRuangan(crommosom[cro])
    cd = len(cd_clashes)
    cr = len(cr_clashes)

    objectFitnes = {
        'rumus': f"1/(1+{cd}+{cr})",
        'nilai': 1/(1+cd+cr),
        'clash': {'cd': cd_clashes, 'cr': cr_clashes},
        'all_clash': unique({**cd_clashes, **cr_clashes})
    }

    if objectFitnes['nilai'] == 1:
        success = True

    if objectFitnes['nilai'] > best_fitness:
        best_fitness = objectFitnes['nilai']
        best_cromosom = cro

    fitness[cro] = objectFitnes
    return objectFitnes

def checkClashDosen(_cromosom):
    result = {}
    for i in range(len(_cromosom)-1):
        for j in range(i+1, len(_cromosom)):
            dosen1 = kuliah[_cromosom[i]['kuliah']]['dosen']
            dosen2 = kuliah[_cromosom[j]['kuliah']]['dosen']
            waktu1 = _cromosom[i]['waktu']
            waktu2 = _cromosom[j]['waktu']
            if dosen1 == dosen2:
                if isCheckTimeClash(_cromosom[i], _cromosom[j]) or not checkPreferensiDosen(dosen1, waktu1):
                    result[i] = i
            if checkTidakBisaWaktuDosen(dosen1, waktu1) or checkTidakBisaWaktuDosen(dosen2, waktu2):
                result[i] = i
    return result

def getProbability():
    global probability
    print("\nProses(3) Melakukan Seleksi (Metode Roulette Wheel)")
    print("1. Menghitung Nilai Probability\n")

    probability = [fit['nilai'] / total_fitness for fit in fitness]
    for i, prob in enumerate(probability):
        print(f"P[{i}] = {prob}")
    print(f"\nTotal Probability = {arraySum(probability)}")

    return probability

def checkClashRuangan(_cromosom):
    result = {}
    for i in range(len(_cromosom)-1):
        for j in range(i+1, len(_cromosom)):
            if ruangan[_cromosom[i]['ruang']][1] == ruangan[_cromosom[j]['ruang']][1]:
                if isCheckTimeClash(_cromosom[i], _cromosom[j]):
                    result[i] = i
    return result

def getCromosomProbability():
    getProbability()
    global cromosom_probability
    cromosom_probability = []
    print("\n2. Menentukan Nilai Probability Kumulatif\n")
    value = 0
    for i in range(len(probability)):
        value += probability[i]
        cromosom_probability.append(value)
        print(f"PK[{i}]={cromosom_probability[i]}")
    return cromosom_probability

def getSeleksi(rand):
    for i, prob in enumerate(cromosom_probability):
        if rand <= prob:
            return i

def seleksi():
    getRandom()
    print("\n4. Proses Seleksi\n")
    newCrosom = []
    for i, value in enumerate(randomValue):
        selection = getSeleksi(value)
        newCrosom.append(crommosom[selection])
        print(f"K[{i}] = K[{selection}]")
        fitness[i] = fitness[selection]

    for i, value in enumerate(newCrosom):
        crommosom[i] = value
        calculate_fitness(i)

def crossover():
    print("\n(4) Melakukan Proses Crossover (Kawin Silang Antar Kromosom)")
    global parent
    parent = []
    crossover_prob = crossover_rate / 100
    print("1. Nilai Crossover Rate =", crossover_prob)
    print(f"2. Generate Random Nilai (0-1), Jika Nilai Random < {crossover_prob} pilih sebagai Parent")

    for i in range(len(crommosom)):
        acak = random.random()
        if acak <= crossover_prob:
            parent.append(i)
            print(f"Select Individu ke-{i} As parent")
        else:
            print(Fore.RED + f"R[{i}] = {acak}")
            print(Style.RESET_ALL)

    for i in range(len(parent)):
        print(f"Parent[{i}] = {parent[i]}")

    if len(parent) > 1:
        newCrosom = [None] * jml_kromosom
        for i in range(len(parent)-1):
            newCrosom[parent[i]] = getCrossover(parent[i], parent[i+1])

        newCrosom[parent[-1]] = getCrossover(parent[-1], parent[0])
        for i, value in enumerate(newCrosom):
            if value is not None:
                crommosom[i] = newCrosom[i]
                calculate_fitness(i)

def getCrossover(index1, index2):
    cro1 = crommosom[index1]
    cro2 = crommosom[index2]

    offspring = random.randint(0, len(cro1)-2)
    newCromosom = cro1[:offspring+1] + cro2[offspring+1:]
    print(f"Posisi Kromosom yang akan dicrossover: {offspring}")
    return newCromosom

def mutation():
    print("\n(5) Melakukan Proses Mutation (Mutasi)")
    gen_per_cro = len(kuliah)
    totalGen = len(crommosom) * gen_per_cro
    print(38 * "-")
    print(f"Total Kromsom: {totalGen}")
    totalMutation = math.ceil(mutation_rate/100 * totalGen)
    print("Total Mutations =", totalMutation)
    print(38 * "-")

    for _ in range(1, totalMutation + 1):
        indexCro = returnIndexList(crommosom)
        if fitness[indexCro].get('all_clash'):
            indexGen = returnIndexList(fitness[indexCro]['all_clash'])
            indexGen = fitness[indexCro]['all_clash'][indexGen]
        else:
            indexGen = returnIndexList(crommosom[indexCro])

        crommosom[indexCro][indexGen]['waktu'] = random.randint(0, len(waktu)-1)
        crommosom[indexCro][indexGen]['ruang'] = random.randint(0, len(ruangan)-1)

        calculate_fitness(indexCro)
        if success:
            break

def generateCromosom():
    for i in range(jml_kromosom):
        crommosom[i] = get_rand_crommosom(kuliah, waktu, ruangan)
        fitness[i] = 0

def calculate_all_fitness():
    for i in range(len(crommosom)):
        calculate_fitness(i)

def cek_jadwal_kosong(crommosom, waktu, ruangan):
    jadwal_terisi = set()
    for cro in crommosom:
        for gen in cro.values():
            jadwal_terisi.add((gen['waktu'], gen['ruang']))
    
    jadwal_kosong = []
    for w in range(len(waktu)):
        for r in range(len(ruangan)):
            if (w, r) not in jadwal_terisi:
                jadwal_kosong.append((w, r))
    
    return jadwal_kosong

def ubah_jadwal_dosen(crommosom, dosen, jadwal_baru):
    for cro in crommosom:
        for gen in cro.values():
            if kuliah[gen['kuliah']]['dosen'] == dosen:
                gen['waktu'] = jadwal_baru[0]
                gen['ruang'] = jadwal_baru[1]
                return

def sarankan_jadwal_kosong(crommosom, waktu, ruangan):
    jadwal_kosong = cek_jadwal_kosong(crommosom, waktu, ruangan)
    if jadwal_kosong:
        return jadwal_kosong[0]  # Saran jadwal kosong pertama
    else:
        return None

# Proses Keajaiban Terjadi
start_time = perf_counter()
generateCromosom()
while generataion < max_generataion and not success:
    generataion += 1
    print(f"\nGenerasi ke-{generataion}")
    calculate_all_fitness()
    showFitness()
    if not success:
        getCromosomProbability()
        seleksi()
    if not success:
        crossover()
    if not success:
        mutation()
end_time = perf_counter()

print("\nCROMOSSOM TERBAIK:")
clash = {**fitness[best_cromosom]['clash']['cr'], **fitness[best_cromosom]['clash']['cd']}
arr = []

for i, val in enumerate(crommosom[best_cromosom]):
    newval = list(val.values())
    values = ' , '.join(str(v) for v in newval)
    if i in clash:
        arr.append(f"Danger : [{values}]")
    else:
        arr.append(f"[{values}]")

arrjoin = ' , '.join(arr)
print(f"Individu[{best_cromosom}]: ( {arrjoin} )")
print('\n\nRAM usage is {} MB(Megabytes)'.format(int(get_ram_usage() / 1024 / 1024)))
print('Elapsed wall clock time = %g seconds.' % (end_time - start_time))

# Contoh penggunaan ubah jadwal dan saran jadwal kosong
dosen_yang_ingin_ubah = 'Dr. A'
jadwal_baru = sarankan_jadwal_kosong(crommosom, waktu, ruangan)
if jadwal_baru:
    print(f"Dosen {dosen_yang_ingin_ubah} disarankan untuk pindah ke jadwal kosong: {jadwal_baru}")
    ubah_jadwal_dosen(crommosom, dosen_yang_ingin_ubah, jadwal_baru)
    calculate_all_fitness()
else:
    print(f"Tidak ada jadwal kosong untuk Dosen {dosen_yang_ingin_ubah}")
