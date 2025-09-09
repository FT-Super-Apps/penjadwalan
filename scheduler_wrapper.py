#!/usr/bin/env python3

import json
import random
import math
from time import perf_counter
from typing import Dict, List, Any, Tuple
from dbConfig import get_schedule_data

class UniversityScheduler:
    """
    University Scheduling System using Genetic Algorithm
    Clean wrapper for web integration with existing database structure
    """
    
    def __init__(self):
        """Initialize scheduler with default parameters"""
        self.population_size = 8
        self.max_generations = 100
        self.crossover_rate = 0.75
        self.mutation_rate = 0.25
        self.per_sks = 50  # minutes per SKS
        
        # Load data from database
        self.data = get_schedule_data()
        self.process_data()
        
    def process_data(self):
        """Process database data for algorithm consumption"""
        # Process kuliah data
        self.kuliah = []
        for k in self.data['kuliah']:
            self.kuliah.append({
                'id': k['kode_kuliah'],
                'nama': k['kode_matakuliah'],
                'kelas': k['nama_kelas'],
                'dosen': k['nama_dosen'],
                'sks': int(k['sks']),
                'prodi': k['kode_prodi'],
                'duration': int(k['sks']) * self.per_sks  # duration in minutes
            })
        
        # Process waktu data (create time mapping)
        self.waktu = []
        for w in self.data['waktu']:
            self.waktu.append({
                'id': int(w['kode_waktu']),
                'hari': w['nama_hari'],
                'jam': w['waktu'],
                'hari_index': self.get_day_index(w['nama_hari']),
                'jam_index': self.get_time_slot_index(int(w['kode_waktu']))
            })
        
        # Process ruangan data
        self.ruangan = []
        for r in self.data['ruangan']:
            self.ruangan.append({
                'id': int(r['id']),
                'nama': r['nama_ruangan']
            })
        
        # Process preferences
        self.preferensi_dosen = {}
        for pref in self.data.get('preferences', []):
            dosen_nama = pref['nama_dosen']
            if dosen_nama not in self.preferensi_dosen:
                self.preferensi_dosen[dosen_nama] = {'suka': [], 'tidak_bisa': []}
            
            # Parse JSON arrays
            try:
                waktu_suka = json.loads(pref['waktu_suka']) if pref['waktu_suka'] else []
                waktu_tidak_bisa = json.loads(pref['waktu_tidak_bisa']) if pref['waktu_tidak_bisa'] else []
                
                self.preferensi_dosen[dosen_nama]['suka'].extend(waktu_suka)
                self.preferensi_dosen[dosen_nama]['tidak_bisa'].extend(waktu_tidak_bisa)
            except:
                continue
    
    def get_day_index(self, hari: str) -> int:
        """Convert day name to index"""
        days = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        return days.index(hari) if hari in days else 0
    
    def get_time_slot_index(self, kode_waktu: int) -> int:
        """Convert time code to slot index within a day"""
        # Assuming 7 slots per day, calculate slot within day
        return ((kode_waktu - 1) % 7)
    
    def create_individual(self) -> List[Dict]:
        """Create a random schedule individual"""
        individual = []
        
        for kuliah in self.kuliah:
            # Randomly assign time and room
            waktu_id = random.choice([w['id'] for w in self.waktu])
            ruangan_id = random.choice([r['id'] for r in self.ruangan])
            
            gene = {
                'kuliah_id': kuliah['id'],
                'kuliah_data': kuliah,
                'waktu_id': waktu_id,
                'ruangan_id': ruangan_id
            }
            individual.append(gene)
        
        return individual
    
    def create_population(self) -> List[List[Dict]]:
        """Create initial population"""
        population = []
        for _ in range(self.population_size):
            population.append(self.create_individual())
        return population
    
    def calculate_fitness(self, individual: List[Dict]) -> Dict[str, Any]:
        """Calculate fitness score for an individual with strict conflict detection"""
        conflicts = {
            'room_time_conflicts': 0,
            'dosen_time_conflicts': 0,
            'preference_violations': 0,
            'room_only_conflicts': 0,
            'time_only_conflicts': 0
        }
        
        penalty = 0
        detailed_conflicts = []
        
        # Create time-room and time-dosen mapping for conflict detection
        time_room_map = {}
        time_dosen_map = {}
        
        for i, gene in enumerate(individual):
            waktu_id = gene['waktu_id']
            ruangan_id = gene['ruangan_id']
            dosen = gene['kuliah_data']['dosen']
            kuliah_info = f"{gene['kuliah_data']['nama']} - {gene['kuliah_data']['kelas']}"
            
            # Check room-time conflicts
            time_room_key = f"{waktu_id}_{ruangan_id}"
            if time_room_key in time_room_map:
                conflicts['room_time_conflicts'] += 1
                penalty += 500  # High penalty for room conflicts
                detailed_conflicts.append({
                    'type': 'room_time',
                    'time': waktu_id,
                    'room': ruangan_id,
                    'classes': [time_room_map[time_room_key], kuliah_info]
                })
            else:
                time_room_map[time_room_key] = kuliah_info
            
            # Check dosen-time conflicts
            time_dosen_key = f"{waktu_id}_{dosen}"
            if time_dosen_key in time_dosen_map:
                conflicts['dosen_time_conflicts'] += 1
                penalty += 400  # High penalty for dosen conflicts
                detailed_conflicts.append({
                    'type': 'dosen_time',
                    'time': waktu_id,
                    'dosen': dosen,
                    'classes': [time_dosen_map[time_dosen_key], kuliah_info]
                })
            else:
                time_dosen_map[time_dosen_key] = kuliah_info
        
        # Check additional conflicts with detailed analysis
        for i, gene1 in enumerate(individual):
            for j, gene2 in enumerate(individual[i+1:], i+1):
                # Same room, different time (room utilization tracking)
                if (gene1['ruangan_id'] == gene2['ruangan_id'] and 
                    gene1['waktu_id'] != gene2['waktu_id']):
                    # This is actually good - room is used efficiently
                    penalty -= 1  # Small bonus
                
                # Same time, different room (check for dosen conflicts we might have missed)
                if (gene1['waktu_id'] == gene2['waktu_id'] and 
                    gene1['ruangan_id'] != gene2['ruangan_id']):
                    if gene1['kuliah_data']['dosen'] == gene2['kuliah_data']['dosen']:
                        # This should already be caught above, but double-check
                        conflicts['dosen_time_conflicts'] += 1
                        penalty += 400
        
        # Check preference violations
        for gene in individual:
            dosen = gene['kuliah_data']['dosen']
            waktu_id = gene['waktu_id']
            
            if dosen in self.preferensi_dosen:
                prefs = self.preferensi_dosen[dosen]
                
                # Heavy penalty for scheduling at blocked times
                if waktu_id in prefs.get('tidak_bisa', []):
                    conflicts['preference_violations'] += 1
                    penalty += 300
                    detailed_conflicts.append({
                        'type': 'preference_blocked',
                        'dosen': dosen,
                        'time': waktu_id,
                        'class': f"{gene['kuliah_data']['nama']} - {gene['kuliah_data']['kelas']}"
                    })
                
                # Bonus for preferred times
                elif waktu_id in prefs.get('suka', []):
                    penalty -= 20  # Increased bonus
        
        # Calculate fitness (higher is better, so we invert penalty)
        base_score = 1000
        fitness_score = max(0, base_score - penalty)
        
        # Extra penalty for any conflicts to strongly discourage them
        total_critical_conflicts = (conflicts['room_time_conflicts'] + 
                                  conflicts['dosen_time_conflicts'])
        if total_critical_conflicts > 0:
            fitness_score = max(0, fitness_score - (total_critical_conflicts * 100))
        
        return {
            'fitness': fitness_score,
            'penalty': penalty,
            'conflicts': conflicts,
            'total_conflicts': sum(conflicts.values()),
            'critical_conflicts': total_critical_conflicts,
            'detailed_conflicts': detailed_conflicts,
            'conflict_free': total_critical_conflicts == 0
        }
    
    def crossover(self, parent1: List[Dict], parent2: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """Perform crossover between two parents"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        # Single point crossover
        crossover_point = random.randint(1, len(parent1) - 1)
        
        child1 = parent1[:crossover_point] + parent2[crossover_point:]
        child2 = parent2[:crossover_point] + parent1[crossover_point:]
        
        return child1, child2
    
    def mutate(self, individual: List[Dict]) -> List[Dict]:
        """Perform smart mutation with conflict resolution"""
        mutated = [gene.copy() for gene in individual]
        
        # First, identify conflicts
        fitness_data = self.calculate_fitness(mutated)
        
        # If there are critical conflicts, try to resolve them first
        if fitness_data['critical_conflicts'] > 0:
            self.resolve_conflicts(mutated)
        
        # Then perform random mutations
        for i, gene in enumerate(mutated):
            if random.random() < self.mutation_rate:
                # Smart mutation: try to avoid creating new conflicts
                self.smart_mutate_gene(mutated, i)
        
        return mutated
    
    def resolve_conflicts(self, individual: List[Dict]) -> None:
        """Resolve conflicts in an individual by reassigning conflicted genes"""
        conflicts_found = True
        attempts = 0
        max_attempts = len(individual) * 2
        
        while conflicts_found and attempts < max_attempts:
            conflicts_found = False
            attempts += 1
            
            # Build conflict maps
            time_room_usage = {}
            time_dosen_usage = {}
            
            for i, gene in enumerate(individual):
                waktu_id = gene['waktu_id']
                ruangan_id = gene['ruangan_id']
                dosen = gene['kuliah_data']['dosen']
                
                # Track room-time usage
                time_room_key = f"{waktu_id}_{ruangan_id}"
                if time_room_key not in time_room_usage:
                    time_room_usage[time_room_key] = []
                time_room_usage[time_room_key].append(i)
                
                # Track dosen-time usage
                time_dosen_key = f"{waktu_id}_{dosen}"
                if time_dosen_key not in time_dosen_usage:
                    time_dosen_usage[time_dosen_key] = []
                time_dosen_usage[time_dosen_key].append(i)
            
            # Resolve room-time conflicts
            for key, gene_indices in time_room_usage.items():
                if len(gene_indices) > 1:
                    conflicts_found = True
                    # Keep first gene, reassign others
                    for gene_idx in gene_indices[1:]:
                        self.reassign_gene(individual, gene_idx, 'room')
            
            # Resolve dosen-time conflicts
            for key, gene_indices in time_dosen_usage.items():
                if len(gene_indices) > 1:
                    conflicts_found = True
                    # Keep first gene, reassign others
                    for gene_idx in gene_indices[1:]:
                        self.reassign_gene(individual, gene_idx, 'time')
    
    def reassign_gene(self, individual: List[Dict], gene_index: int, conflict_type: str) -> None:
        """Reassign a gene to resolve conflicts"""
        gene = individual[gene_index]
        max_tries = 20
        
        for _ in range(max_tries):
            if conflict_type == 'room':
                # Try different room
                new_room_id = random.choice([r['id'] for r in self.ruangan])
                temp_gene = gene.copy()
                temp_gene['ruangan_id'] = new_room_id
                
                # Check if this resolves the conflict
                if not self.has_room_conflict(individual, gene_index, temp_gene):
                    individual[gene_index]['ruangan_id'] = new_room_id
                    break
                    
            elif conflict_type == 'time':
                # Try different time
                new_waktu_id = random.choice([w['id'] for w in self.waktu])
                temp_gene = gene.copy()
                temp_gene['waktu_id'] = new_waktu_id
                
                # Check if this resolves the conflict and respects preferences
                if not self.has_time_conflict(individual, gene_index, temp_gene):
                    individual[gene_index]['waktu_id'] = new_waktu_id
                    break
    
    def has_room_conflict(self, individual: List[Dict], exclude_index: int, test_gene: Dict) -> bool:
        """Check if a gene would create room conflicts"""
        for i, other_gene in enumerate(individual):
            if i == exclude_index:
                continue
            if (other_gene['waktu_id'] == test_gene['waktu_id'] and 
                other_gene['ruangan_id'] == test_gene['ruangan_id']):
                return True
        return False
    
    def has_time_conflict(self, individual: List[Dict], exclude_index: int, test_gene: Dict) -> bool:
        """Check if a gene would create time conflicts (dosen or preference)"""
        dosen = test_gene['kuliah_data']['dosen']
        waktu_id = test_gene['waktu_id']
        
        # Check dosen conflict
        for i, other_gene in enumerate(individual):
            if i == exclude_index:
                continue
            if (other_gene['kuliah_data']['dosen'] == dosen and 
                other_gene['waktu_id'] == waktu_id):
                return True
        
        # Check preference violation
        if dosen in self.preferensi_dosen:
            if waktu_id in self.preferensi_dosen[dosen].get('tidak_bisa', []):
                return True
        
        return False
    
    def smart_mutate_gene(self, individual: List[Dict], gene_index: int) -> None:
        """Perform smart mutation that tries to avoid conflicts"""
        gene = individual[gene_index]
        mutation_options = []
        
        # Try different rooms first (usually less restrictive)
        for room in self.ruangan:
            temp_gene = gene.copy()
            temp_gene['ruangan_id'] = room['id']
            if not self.has_room_conflict(individual, gene_index, temp_gene):
                mutation_options.append(('room', room['id']))
        
        # Try different times (more restrictive due to dosen conflicts)
        for waktu in self.waktu:
            temp_gene = gene.copy()
            temp_gene['waktu_id'] = waktu['id']
            if not self.has_time_conflict(individual, gene_index, temp_gene):
                mutation_options.append(('time', waktu['id']))
        
        # Apply a random valid mutation if available
        if mutation_options:
            mutation_type, new_value = random.choice(mutation_options)
            if mutation_type == 'room':
                individual[gene_index]['ruangan_id'] = new_value
            else:
                individual[gene_index]['waktu_id'] = new_value
        else:
            # Fallback to random mutation if no conflict-free option
            if random.random() < 0.5:
                individual[gene_index]['ruangan_id'] = random.choice([r['id'] for r in self.ruangan])
            else:
                individual[gene_index]['waktu_id'] = random.choice([w['id'] for w in self.waktu])
    
    def select_parents(self, population: List[List[Dict]], fitness_scores: List[Dict]) -> List[List[Dict]]:
        """Select parents using tournament selection"""
        parents = []
        
        for _ in range(2):
            # Tournament selection
            tournament_size = 3
            tournament = random.sample(list(zip(population, fitness_scores)), 
                                     min(tournament_size, len(population)))
            winner = max(tournament, key=lambda x: x[1]['fitness'])
            parents.append(winner[0])
        
        return parents
    
    def generate_schedule(self, progress_callback=None) -> Dict[str, Any]:
        """
        Generate schedule using genetic algorithm
        
        Args:
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Dictionary containing best schedule and metadata
        """
        start_time = perf_counter()
        
        # Create initial population
        population = self.create_population()
        best_individual = None
        best_fitness = -1
        generation_data = []
        
        for generation in range(self.max_generations):
            # Calculate fitness for all individuals
            fitness_scores = []
            for individual in population:
                fitness_data = self.calculate_fitness(individual)
                fitness_scores.append(fitness_data)
                
                # Track best individual
                if fitness_data['fitness'] > best_fitness:
                    best_fitness = fitness_data['fitness']
                    best_individual = individual.copy()
            
            # Store generation data
            avg_fitness = sum(f['fitness'] for f in fitness_scores) / len(fitness_scores)
            generation_data.append({
                'generation': generation,
                'best_fitness': best_fitness,
                'avg_fitness': avg_fitness,
                'total_conflicts': min(f['total_conflicts'] for f in fitness_scores)
            })
            
            # Progress callback
            if progress_callback:
                progress_callback({
                    'generation': generation + 1,
                    'max_generations': self.max_generations,
                    'best_fitness': best_fitness,
                    'avg_fitness': avg_fitness,
                    'progress': (generation + 1) / self.max_generations * 100
                })
            
            # Early termination if good solution found
            if best_fitness >= 950:  # Adjust threshold as needed
                break
            
            # Create new population
            new_population = []
            
            # Elitism - keep best individual
            new_population.append(best_individual.copy())
            
            # Generate rest of population
            while len(new_population) < self.population_size:
                parents = self.select_parents(population, fitness_scores)
                child1, child2 = self.crossover(parents[0], parents[1])
                
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        end_time = perf_counter()
        execution_time = end_time - start_time
        
        # Format final schedule
        formatted_schedule = self.format_schedule(best_individual)
        final_fitness = self.calculate_fitness(best_individual)
        
        # Validate final schedule
        validation_result = self.validate_schedule(best_individual)
        
        return {
            'success': True,
            'schedule': formatted_schedule,
            'metadata': {
                'generations': len(generation_data),
                'best_fitness': best_fitness,
                'final_conflicts': final_fitness['conflicts'],
                'execution_time': round(execution_time, 2),
                'total_kuliah': len(self.kuliah),
                'conflict_free': final_fitness['conflict_free'],
                'validation': validation_result,
                'algorithm_params': {
                    'population_size': self.population_size,
                    'max_generations': self.max_generations,
                    'crossover_rate': self.crossover_rate,
                    'mutation_rate': self.mutation_rate
                }
            },
            'generation_data': generation_data,
            'detailed_conflicts': final_fitness.get('detailed_conflicts', [])
        }
    
    def validate_schedule(self, individual: List[Dict]) -> Dict[str, Any]:
        """Validate the final schedule for conflicts"""
        validation = {
            'is_valid': True,
            'room_conflicts': [],
            'dosen_conflicts': [],
            'preference_violations': [],
            'total_violations': 0
        }
        
        # Check room conflicts
        time_room_map = {}
        for gene in individual:
            key = f"{gene['waktu_id']}_{gene['ruangan_id']}"
            if key not in time_room_map:
                time_room_map[key] = []
            time_room_map[key].append({
                'kuliah': gene['kuliah_data']['nama'],
                'kelas': gene['kuliah_data']['kelas'],
                'dosen': gene['kuliah_data']['dosen']
            })
        
        for key, classes in time_room_map.items():
            if len(classes) > 1:
                waktu_id, ruangan_id = key.split('_')
                waktu_detail = next((w for w in self.waktu if w['id'] == int(waktu_id)), None)
                ruangan_detail = next((r for r in self.ruangan if r['id'] == int(ruangan_id)), None)
                
                validation['room_conflicts'].append({
                    'time': waktu_detail['jam'] if waktu_detail else waktu_id,
                    'day': waktu_detail['hari'] if waktu_detail else 'Unknown',
                    'room': ruangan_detail['nama'] if ruangan_detail else ruangan_id,
                    'classes': classes
                })
                validation['is_valid'] = False
        
        # Check dosen conflicts
        time_dosen_map = {}
        for gene in individual:
            key = f"{gene['waktu_id']}_{gene['kuliah_data']['dosen']}"
            if key not in time_dosen_map:
                time_dosen_map[key] = []
            time_dosen_map[key].append({
                'kuliah': gene['kuliah_data']['nama'],
                'kelas': gene['kuliah_data']['kelas'],
                'ruangan_id': gene['ruangan_id']
            })
        
        for key, classes in time_dosen_map.items():
            if len(classes) > 1:
                waktu_id, dosen = key.split('_', 1)
                waktu_detail = next((w for w in self.waktu if w['id'] == int(waktu_id)), None)
                
                validation['dosen_conflicts'].append({
                    'time': waktu_detail['jam'] if waktu_detail else waktu_id,
                    'day': waktu_detail['hari'] if waktu_detail else 'Unknown',
                    'dosen': dosen,
                    'classes': classes
                })
                validation['is_valid'] = False
        
        # Check preference violations
        for gene in individual:
            dosen = gene['kuliah_data']['dosen']
            waktu_id = gene['waktu_id']
            
            if dosen in self.preferensi_dosen:
                prefs = self.preferensi_dosen[dosen]
                if waktu_id in prefs.get('tidak_bisa', []):
                    waktu_detail = next((w for w in self.waktu if w['id'] == waktu_id), None)
                    
                    validation['preference_violations'].append({
                        'dosen': dosen,
                        'time': waktu_detail['jam'] if waktu_detail else str(waktu_id),
                        'day': waktu_detail['hari'] if waktu_detail else 'Unknown',
                        'kuliah': gene['kuliah_data']['nama'],
                        'kelas': gene['kuliah_data']['kelas']
                    })
                    validation['is_valid'] = False
        
        validation['total_violations'] = (len(validation['room_conflicts']) + 
                                        len(validation['dosen_conflicts']) + 
                                        len(validation['preference_violations']))
        
        return validation
    
    def format_schedule(self, individual: List[Dict]) -> List[Dict]:
        """Format schedule for web display"""
        formatted = []
        
        for gene in individual:
            # Find waktu and ruangan details
            waktu_detail = next((w for w in self.waktu if w['id'] == gene['waktu_id']), None)
            ruangan_detail = next((r for r in self.ruangan if r['id'] == gene['ruangan_id']), None)
            
            formatted_gene = {
                'kuliah_id': gene['kuliah_id'],
                'kode_matakuliah': gene['kuliah_data']['nama'],
                'nama_kelas': gene['kuliah_data']['kelas'],
                'dosen': gene['kuliah_data']['dosen'],
                'sks': gene['kuliah_data']['sks'],
                'prodi': gene['kuliah_data']['prodi'],
                'hari': waktu_detail['hari'] if waktu_detail else 'Unknown',
                'waktu': waktu_detail['jam'] if waktu_detail else 'Unknown',
                'ruangan': ruangan_detail['nama'] if ruangan_detail else 'Unknown',
                'waktu_id': gene['waktu_id'],
                'ruangan_id': gene['ruangan_id']
            }
            formatted.append(formatted_gene)
        
        # Sort by day and time for better display
        day_order = ['SENIN', 'SELASA', 'RABU', 'KAMIS', 'JUMAT', 'SABTU']
        formatted.sort(key=lambda x: (
            day_order.index(x['hari']) if x['hari'] in day_order else 6,
            x['waktu']
        ))
        
        return formatted
    
    def get_schedule_summary(self, schedule: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics for a schedule"""
        if not schedule:
            return {}
        
        # Group by day
        by_day = {}
        for item in schedule:
            day = item['hari']
            if day not in by_day:
                by_day[day] = []
            by_day[day].append(item)
        
        # Count by dosen
        by_dosen = {}
        for item in schedule:
            dosen = item['dosen']
            by_dosen[dosen] = by_dosen.get(dosen, 0) + 1
        
        # Count by ruangan
        by_ruangan = {}
        for item in schedule:
            ruangan = item['ruangan']
            by_ruangan[ruangan] = by_ruangan.get(ruangan, 0) + 1
        
        return {
            'total_classes': len(schedule),
            'days_used': list(by_day.keys()),
            'classes_per_day': {day: len(classes) for day, classes in by_day.items()},
            'classes_per_dosen': by_dosen,
            'classes_per_ruangan': by_ruangan,
            'unique_dosen': len(by_dosen),
            'unique_ruangan': len(by_ruangan)
        }