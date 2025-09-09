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

# Enhanced preference system
preferensi_dosen_enhanced = {
    'Dr. Ahmad': {
        'reserved_slots': [{'waktu': 1, 'ruang': 0, 'priority': 'exclusive', 'reason': 'Research meeting'}],
        'preferred_slots': [{'waktu': 2}, {'waktu': 3}],
        'blocked_slots': [{'waktu': 8, 'reason': 'Administrative duty'}]
    },
    'Dr. Budi': {
        'reserved_slots': [{'waktu': 5, 'ruang': 1, 'priority': 'exclusive', 'reason': 'Senior faculty privilege'}],
        'preferred_slots': [{'waktu': 6}],
        'blocked_slots': []
    }
}

# Global reserved schedule tracking
reserved_schedule = {}
preference_weights = {
    'exclusive': 1000,
    'preferred': 30,
    'blocked': 50
}

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

    # Initialize timeClash entries if they don't exist
    if clash1 not in timeClash:
        timeClash[clash1] = {}
    if clash2 not in timeClash:
        timeClash[clash2] = {}

    # Check if we already calculated this clash
    if clash2 in timeClash[clash1]:
        return timeClash[clash1][clash2]

    waktu1 = waktu[gen1['waktu']]
    waktu2 = waktu[gen2['waktu']]
    bentrok = 0

    if gen1['waktu'] == gen2['waktu']:
        bentrok = 1
    elif waktu1[1] == waktu2[1]:  # Same day
        sks1 = int(kuliah[gen1['kuliah']]['sks'])
        sks2 = int(kuliah[gen2['kuliah']]['sks'])
        awalJadwal1 = stringToSecond(waktu1[2])
        akhirJadwal1 = awalJadwal1 + sks1 * per_sks * 60
        awalJadwal2 = stringToSecond(waktu2[2])
        akhirJadwal2 = awalJadwal2 + sks2 * per_sks * 60
        
        # Check for time overlap
        if (awalJadwal1 < akhirJadwal2 and akhirJadwal1 > awalJadwal2):
            bentrok = 1

    # Store the result for both directions
    timeClash[clash1][clash2] = bentrok
    timeClash[clash2][clash1] = bentrok

    return bentrok

def checkPreferensiDosen(dosen, waktu):
    if dosen in preferensi_dosen:
        return waktu in preferensi_dosen[dosen]['preferensi_waktu']
    return False

def checkTidakBisaWaktuDosen(dosen, waktu):
    if dosen in preferensi_dosen:
        return waktu in preferensi_dosen[dosen]['tidak_bisa_waktu']
    return False

def pre_allocate_reserved_slots():
    """Pre-allocate exclusive time slots before GA starts"""
    global reserved_schedule
    reserved_schedule = {}
    
    for dosen, prefs in preferensi_dosen_enhanced.items():
        for slot in prefs.get('reserved_slots', []):
            waktu_idx = slot['waktu']
            ruang_idx = slot.get('ruang', 'any')
            
            if ruang_idx == 'any':
                # Reserve time slot for any room
                key = f"waktu_{waktu_idx}_any"
            else:
                # Reserve specific time and room
                key = f"waktu_{waktu_idx}_ruang_{ruang_idx}"
            
            reserved_schedule[key] = {
                'dosen': dosen,
                'priority': slot['priority'],
                'reason': slot.get('reason', 'Reserved slot')
            }
    
    print(f"Pre-allocated {len(reserved_schedule)} reserved slots")
    return reserved_schedule

def is_slot_reserved(waktu_idx, ruang_idx=None):
    """Check if a time slot is reserved"""
    if ruang_idx is not None:
        key = f"waktu_{waktu_idx}_ruang_{ruang_idx}"
        if key in reserved_schedule:
            return reserved_schedule[key]
    
    # Check for any-room reservation
    key_any = f"waktu_{waktu_idx}_any"
    if key_any in reserved_schedule:
        return reserved_schedule[key_any]
    
    return None

def check_reserved_violations(kromosom_data):
    """Check violations of reserved slots"""
    violations = []
    
    for gen_idx, gen in kromosom_data.items():
        waktu_idx = gen['waktu']
        ruang_idx = gen['ruang']
        kuliah_dosen = kuliah[gen['kuliah']]['dosen']
        
        reservation = is_slot_reserved(waktu_idx, ruang_idx)
        if reservation:
            # Slot is reserved, check if current dosen is the owner
            if reservation['dosen'] != kuliah_dosen:
                violations.append({
                    'gen_idx': gen_idx,
                    'violation_type': 'reserved_slot_conflict',
                    'reserved_by': reservation['dosen'],
                    'attempted_by': kuliah_dosen,
                    'penalty_weight': preference_weights['exclusive']
                })
    
    return violations

def check_preference_violations(kromosom_data):
    """Check violations of lecturer preferences"""
    violations = []
    
    for gen_idx, gen in kromosom_data.items():
        waktu_idx = gen['waktu']
        kuliah_dosen = kuliah[gen['kuliah']]['dosen']
        
        if kuliah_dosen in preferensi_dosen_enhanced:
            prefs = preferensi_dosen_enhanced[kuliah_dosen]
            
            # Check blocked slots
            for blocked in prefs.get('blocked_slots', []):
                if blocked['waktu'] == waktu_idx:
                    violations.append({
                        'gen_idx': gen_idx,
                        'violation_type': 'blocked_slot',
                        'reason': blocked.get('reason', 'Blocked time'),
                        'penalty_weight': preference_weights['blocked']
                    })
            
            # Check if not in preferred slots (soft constraint)
            preferred_times = [p['waktu'] for p in prefs.get('preferred_slots', [])]
            if preferred_times and waktu_idx not in preferred_times:
                violations.append({
                    'gen_idx': gen_idx,
                    'violation_type': 'not_preferred',
                    'penalty_weight': preference_weights['preferred']
                })
    
    return violations

def calculate_fitness(cro):
    global objectFitnes, success, best_cromosom, best_fitness, fitness

    # Original clash detection
    cd_clashes = checkClashDosen(crommosom[cro])
    cr_clashes = checkClashRuangan(crommosom[cro])
    cd = len(cd_clashes)
    cr = len(cr_clashes)

    # Enhanced constraint checking
    reserved_violations = check_reserved_violations(crommosom[cro])
    preference_violations = check_preference_violations(crommosom[cro])
    
    # Calculate weighted penalties
    total_penalties = 0
    
    # Hard constraints (reserved slots) - highest penalty
    for violation in reserved_violations:
        total_penalties += violation['penalty_weight']
    
    # Soft constraints (preferences) - medium penalty  
    for violation in preference_violations:
        total_penalties += violation['penalty_weight']
    
    # Original clashes - high penalty
    total_penalties += (cd + cr) * 100

    # Enhanced fitness calculation
    fitness_value = 1 / (1 + total_penalties)
    
    objectFitnes = {
        'rumus': f"1/(1+{total_penalties})",
        'nilai': fitness_value,
        'clash': {'cd': cd_clashes, 'cr': cr_clashes},
        'reserved_violations': reserved_violations,
        'preference_violations': preference_violations,
        'total_penalties': total_penalties,
        'all_clash': unique({**cd_clashes, **cr_clashes})
    }

    # Success criteria: no hard constraints violated and minimal penalties
    if len(reserved_violations) == 0 and cd == 0 and cr == 0:
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
            
            # Enhanced clash detection
            if dosen1 == dosen2:
                if isCheckTimeClash(_cromosom[i], _cromosom[j]):
                    result[i] = i
                    result[j] = j
                    
            # Check reserved slot violations
            if is_slot_reserved(waktu1, _cromosom[i]['ruang']):
                reservation = is_slot_reserved(waktu1, _cromosom[i]['ruang'])
                if reservation['dosen'] != dosen1:
                    result[i] = i
                    
            if is_slot_reserved(waktu2, _cromosom[j]['ruang']):
                reservation = is_slot_reserved(waktu2, _cromosom[j]['ruang'])
                if reservation['dosen'] != dosen2:
                    result[j] = j
            
            # Original preference checks
            if checkTidakBisaWaktuDosen(dosen1, waktu1) or checkTidakBisaWaktuDosen(dosen2, waktu2):
                if checkTidakBisaWaktuDosen(dosen1, waktu1):
                    result[i] = i
                if checkTidakBisaWaktuDosen(dosen2, waktu2):
                    result[j] = j
    
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

    # Convert dictionary to list for crossover
    cro1_list = [cro1[i] for i in range(len(cro1))]
    cro2_list = [cro2[i] for i in range(len(cro2))]
    
    offspring = random.randint(0, len(cro1_list)-2)
    new_list = cro1_list[:offspring+1] + cro2_list[offspring+1:]
    
    # Convert back to dictionary format
    newCromosom = {i: new_list[i] for i in range(len(new_list))}
    
    print(f"Posisi Kromosom yang akan dicrossover: {offspring}")
    return newCromosom

def get_smart_mutation_options(dosen, current_waktu, current_ruang):
    """Get intelligent mutation options based on lecturer preferences"""
    options = []
    
    if dosen in preferensi_dosen_enhanced:
        prefs = preferensi_dosen_enhanced[dosen]
        
        # Priority 1: Preferred slots
        for pref in prefs.get('preferred_slots', []):
            if pref['waktu'] != current_waktu:
                for ruang_idx in range(len(ruangan)):
                    if not is_slot_reserved(pref['waktu'], ruang_idx):
                        options.append({
                            'waktu': pref['waktu'], 
                            'ruang': ruang_idx, 
                            'score': preference_weights['preferred']
                        })
    
    # Priority 2: Any available non-reserved slot
    if not options:
        for waktu_idx in range(len(waktu)):
            for ruang_idx in range(len(ruangan)):
                if not is_slot_reserved(waktu_idx, ruang_idx) and waktu_idx != current_waktu:
                    # Skip blocked slots
                    is_blocked = False
                    if dosen in preferensi_dosen_enhanced:
                        blocked_times = [b['waktu'] for b in preferensi_dosen_enhanced[dosen].get('blocked_slots', [])]
                        if waktu_idx in blocked_times:
                            is_blocked = True
                    
                    if not is_blocked:
                        options.append({
                            'waktu': waktu_idx, 
                            'ruang': ruang_idx, 
                            'score': 1
                        })
    
    # Sort by score (higher is better)
    options.sort(key=lambda x: x['score'], reverse=True)
    return options[:5]  # Return top 5 options

def intelligent_mutation():
    print("\n(5) Melakukan Proses Intelligent Mutation")
    gen_per_cro = len(kuliah)
    totalGen = len(crommosom) * gen_per_cro
    print(38 * "-")
    print(f"Total Kromsom: {totalGen}")
    totalMutation = math.ceil(mutation_rate/100 * totalGen)
    print("Total Mutations =", totalMutation)
    print(38 * "-")

    for _ in range(1, totalMutation + 1):
        indexCro = returnIndexList(crommosom)
        
        # Prioritize mutating genes with violations
        target_genes = []
        
        # Add genes with reserved violations (highest priority)
        for violation in fitness[indexCro].get('reserved_violations', []):
            target_genes.append((violation['gen_idx'], 'reserved'))
            
        # Add genes with preference violations
        for violation in fitness[indexCro].get('preference_violations', []):
            target_genes.append((violation['gen_idx'], 'preference'))
            
        # Add genes with clashes
        if fitness[indexCro].get('all_clash'):
            for clash_gen in fitness[indexCro]['all_clash']:
                target_genes.append((clash_gen, 'clash'))
        
        # If no violations, mutate randomly
        if not target_genes:
            indexGen = returnIndexList(crommosom[indexCro])
        else:
            indexGen, violation_type = random.choice(target_genes)
        
        # Get current gene info
        current_gen = crommosom[indexCro][indexGen]
        kuliah_dosen = kuliah[current_gen['kuliah']]['dosen']
        
        # Get smart mutation options
        mutation_options = get_smart_mutation_options(
            kuliah_dosen, 
            current_gen['waktu'], 
            current_gen['ruang']
        )
        
        if mutation_options:
            # Choose from top options with some randomness
            if random.random() < 0.7:  # 70% choose best option
                chosen = mutation_options[0]
            else:  # 30% choose randomly from top options
                chosen = random.choice(mutation_options)
                
            crommosom[indexCro][indexGen]['waktu'] = chosen['waktu']
            crommosom[indexCro][indexGen]['ruang'] = chosen['ruang']
            print(f"Smart mutation: Gen[{indexGen}] -> Waktu[{chosen['waktu']}], Ruang[{chosen['ruang']}], Score: {chosen['score']}")
        else:
            # Fallback to random mutation
            crommosom[indexCro][indexGen]['waktu'] = random.randint(0, len(waktu)-1)
            crommosom[indexCro][indexGen]['ruang'] = random.randint(0, len(ruangan)-1)
            print(f"Random mutation: Gen[{indexGen}]")

        calculate_fitness(indexCro)
        if success:
            print("Success achieved through intelligent mutation!")
            break

def mutation():
    """Wrapper function to choose between intelligent and standard mutation"""
    if preferensi_dosen_enhanced:
        intelligent_mutation()
    else:
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

def validate_schedule_constraints():
    """Validate that reserved slots don't conflict with each other"""
    conflicts = []
    reserved_keys = list(reserved_schedule.keys())
    
    for i, key1 in enumerate(reserved_keys):
        for key2 in reserved_keys[i+1:]:
            res1 = reserved_schedule[key1]
            res2 = reserved_schedule[key2]
            
            # Extract time and room info from keys
            if 'ruang' in key1 and 'ruang' in key2:
                # Both have specific rooms
                time1 = int(key1.split('_')[1])
                room1 = int(key1.split('_')[3])
                time2 = int(key2.split('_')[1])
                room2 = int(key2.split('_')[3])
                
                if time1 == time2 and room1 == room2:
                    conflicts.append({
                        'type': 'same_slot_reserved',
                        'dosen1': res1['dosen'],
                        'dosen2': res2['dosen'],
                        'slot': f"Time {time1}, Room {room1}"
                    })
    
    return conflicts

def display_enhanced_fitness_info():
    """Display detailed fitness information including constraint violations"""
    print(f"\n=== ENHANCED FITNESS ANALYSIS ===")
    for i, fit in enumerate(fitness):
        if fit is None:
            continue
        print(f"\nKromosom[{i}]:")
        print(f"  Total Penalties: {fit.get('total_penalties', 0)}")
        print(f"  Fitness Value: {fit['nilai']:.6f}")
        
        # Reserved violations
        reserved_viol = fit.get('reserved_violations', [])
        if reserved_viol:
            print(f"  Reserved Slot Violations: {len(reserved_viol)}")
            for v in reserved_viol[:3]:  # Show first 3
                print(f"    - Gen[{v['gen_idx']}]: {v['attempted_by']} conflicts with {v['reserved_by']}")
        
        # Preference violations
        pref_viol = fit.get('preference_violations', [])
        if pref_viol:
            print(f"  Preference Violations: {len(pref_viol)}")
            for v in pref_viol[:3]:  # Show first 3
                print(f"    - Gen[{v['gen_idx']}]: {v['violation_type']}")

def get_available_slots_for_dosen(dosen):
    """Get all available time slots for a specific lecturer considering their preferences"""
    available_slots = []
    
    if dosen in preferensi_dosen_enhanced:
        prefs = preferensi_dosen_enhanced[dosen]
        
        # Check all time slots
        for waktu_idx in range(len(waktu)):
            # Skip blocked slots
            is_blocked = any(blocked['waktu'] == waktu_idx for blocked in prefs.get('blocked_slots', []))
            if is_blocked:
                continue
            
            # Check each room
            for ruang_idx in range(len(ruangan)):
                # Skip if slot is reserved by another dosen
                reservation = is_slot_reserved(waktu_idx, ruang_idx)
                if reservation and reservation['dosen'] != dosen:
                    continue
                
                # Determine priority
                priority = 'available'
                score = 1
                
                # Check if it's a preferred slot
                preferred_times = [p['waktu'] for p in prefs.get('preferred_slots', [])]
                if waktu_idx in preferred_times:
                    priority = 'preferred'
                    score = preference_weights['preferred']
                
                available_slots.append({
                    'waktu': waktu_idx,
                    'ruang': ruang_idx,
                    'priority': priority,
                    'score': score
                })
    
    return sorted(available_slots, key=lambda x: x['score'], reverse=True)

# Enhanced Scheduling Process
start_time = perf_counter()

# Step 1: Pre-allocate reserved slots
print("=== INITIALIZING ENHANCED SCHEDULING SYSTEM ===")
pre_allocate_reserved_slots()

# Validate constraints
conflicts = validate_schedule_constraints()
if conflicts:
    print("WARNING: Reserved slot conflicts detected:")
    for conflict in conflicts:
        print(f"  - {conflict['dosen1']} and {conflict['dosen2']} both reserved {conflict['slot']}")

# Step 2: Generate initial population
generateCromosom()

# Step 3: Main GA loop with enhanced features
while generataion < max_generataion and not success:
    generataion += 1
    print(f"\n{'='*50}")
    print(f"GENERASI KE-{generataion}")
    print(f"{'='*50}")
    
    # Calculate fitness with enhanced constraints
    calculate_all_fitness()
    showFitness()
    
    # Display enhanced fitness analysis
    display_enhanced_fitness_info()
    
    if not success:
        getCromosomProbability()
        seleksi()
    if not success:
        crossover()
    if not success:
        mutation()
        
    # Early termination if very good solution found
    if best_fitness > 0.95:
        print(f"\nHigh quality solution found (fitness: {best_fitness:.6f})")
        if generataion > 3:  # Allow at least 3 generations
            break

end_time = perf_counter()

print("\n" + "="*60)
print("HASIL OPTIMASI PENJADWALAN DENGAN ENHANCED SYSTEM")
print("="*60)

print(f"\nKROMOSOM TERBAIK [Fitness: {best_fitness:.6f}]:")
best_fitness_obj = fitness[best_cromosom]
clash = {**best_fitness_obj['clash']['cr'], **best_fitness_obj['clash']['cd']}

# Enhanced result display
reserved_violations = best_fitness_obj.get('reserved_violations', [])
preference_violations = best_fitness_obj.get('preference_violations', [])

arr = []
for i, val in enumerate(crommosom[best_cromosom].values()):
    kuliah_info = kuliah[val['kuliah']]
    waktu_info = waktu[val['waktu']]
    ruang_info = ruangan[val['ruang']]
    
    display_info = f"Kuliah[{val['kuliah']}]:{kuliah_info['nama']} | Dosen:{kuliah_info['dosen']} | Waktu:{waktu_info[1]} {waktu_info[2]} | Ruang:{ruang_info[1]}"
    
    status_indicators = []
    if i in clash:
        status_indicators.append("⚠️ CLASH")
    if any(v['gen_idx'] == i for v in reserved_violations):
        status_indicators.append("🔒 RESERVED VIOLATION")
    if any(v['gen_idx'] == i for v in preference_violations):
        status_indicators.append("📋 PREFERENCE ISSUE")
    
    if status_indicators:
        arr.append(f"{'|'.join(status_indicators)}: {display_info}")
    else:
        arr.append(f"✅ OK: {display_info}")

for item in arr:
    print(f"  {item}")

# Summary statistics
print(f"\n=== CONSTRAINT ANALYSIS ===")
print(f"Reserved Slot Violations: {len(reserved_violations)}")
print(f"Preference Violations: {len(preference_violations)}")
print(f"Traditional Clashes: {len(clash)}")
print(f"Total Penalties: {best_fitness_obj.get('total_penalties', 0)}")

# Show reserved slots status
print(f"\n=== RESERVED SLOTS STATUS ===")
for key, reservation in reserved_schedule.items():
    is_respected = True
    for violation in reserved_violations:
        if violation['reserved_by'] == reservation['dosen']:
            is_respected = False
            break
    
    status = "✅ RESPECTED" if is_respected else "❌ VIOLATED"
    print(f"{status}: {reservation['dosen']} - {key} ({reservation['reason']})")

print('\n=== SYSTEM PERFORMANCE ===')
print('RAM usage: {} MB'.format(int(get_ram_usage() / 1024 / 1024)))
print('Execution time: {:.3f} seconds'.format(end_time - start_time))
print(f'Generations completed: {generataion}')
print(f'Success achieved: {"Yes" if success else "No"}')

# Enhanced schedule recommendation
print(f"\n=== SCHEDULE OPTIMIZATION SUGGESTIONS ===")
for dosen_name in preferensi_dosen_enhanced.keys():
    available_slots = get_available_slots_for_dosen(dosen_name)
    if available_slots:
        top_slot = available_slots[0]
        print(f"{dosen_name}: Best available slot - Time[{top_slot['waktu']}] Room[{top_slot['ruang']}] (Priority: {top_slot['priority']})")
    else:
        print(f"{dosen_name}: No optimal slots available")
