#!/usr/bin/env python3
"""
Enhanced Scheduler - Wrapper class for the enhanced scheduling system
Provides clean interface for web application integration
"""

import math
import random
import psutil
from time import perf_counter
from typing import Dict, List, Any, Callable, Optional

class EnhancedScheduler:
    """
    Enhanced University Scheduling System
    Wraps the genetic algorithm with clean interface for web integration
    """
    
    def __init__(self, data: Dict[str, List], config: Dict[str, Any]):
        """
        Initialize scheduler with data and configuration
        
        Args:
            data: Dictionary containing kuliah, waktu, ruangan, preferensi_dosen
            config: Configuration dictionary with algorithm, preferences, constraints
        """
        self.data = data
        self.config = config
        
        # Extract data
        self.kuliah = data.get('kuliah', [])
        self.waktu = data.get('waktu', [])
        self.ruangan = data.get('ruangan', [])
        self.preferensi_dosen = self._process_preferences(data.get('preferensi_dosen', []))
        
        # Algorithm parameters from config
        algo_config = config.get('algorithm', {})
        self.jml_kromosom = algo_config.get('populationSize', 10)
        self.max_generataion = algo_config.get('maxGenerations', 50)
        self.crossover_rate = algo_config.get('crossoverRate', 75)
        self.mutation_rate = algo_config.get('mutationRate', 25)
        self.per_sks = algo_config.get('minutesPerSks', 50)
        self.early_termination = algo_config.get('earlyTermination', 0.95)
        
        # Preference weights from config
        pref_config = config.get('preferences', {})
        self.preference_weights = {
            'exclusive': pref_config.get('reservedPenalty', 1000),
            'preferred': pref_config.get('preferredPenalty', 30),
            'blocked': pref_config.get('blockedPenalty', 50)
        }
        
        # Enhanced preferences (simplified for web demo)
        self.preferensi_dosen_enhanced = self._create_enhanced_preferences()
        
        # Algorithm state
        self.success = False
        self.fitness = [None] * self.jml_kromosom
        self.total_fitness = 0
        self.crommosom = [None] * self.jml_kromosom
        self.best_fitness = 0
        self.best_cromosom = 0
        self.generataion = 0
        self.timeClash = {}
        self.reserved_schedule = {}
        
        # Statistics tracking
        self.statistics = {
            'start_time': 0,
            'end_time': 0,
            'execution_time': 0,
            'generations_completed': 0,
            'best_fitness': 0,
            'success_achieved': False,
            'total_violations': 0,
            'reserved_violations': 0,
            'preference_violations': 0,
            'clashes': 0,
            'ram_usage_mb': 0
        }
    
    def _process_preferences(self, pref_list: List[Dict]) -> Dict:
        """Convert preference list to dictionary format"""
        result = {}
        for pref in pref_list:
            result[pref['dosen']] = {
                'preferensi_waktu': pref.get('preferensi_waktu', []),
                'tidak_bisa_waktu': pref.get('tidak_bisa_waktu', [])
            }
        return result
    
    def _create_enhanced_preferences(self) -> Dict:
        """Create enhanced preferences from basic preferences"""
        enhanced = {}
        
        for dosen, prefs in self.preferensi_dosen.items():
            enhanced[dosen] = {
                'reserved_slots': [],  # No reserved slots by default
                'preferred_slots': [
                    {'waktu': t} 
                    for t in prefs.get('preferensi_waktu', [])
                ],
                'blocked_slots': [
                    {'waktu': t, 'reason': 'Not available'}
                    for t in prefs.get('tidak_bisa_waktu', [])
                ]
            }
        
        return enhanced
    
    def optimize(self, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Run scheduling optimization
        
        Args:
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary containing results and statistics
        """
        self.statistics['start_time'] = perf_counter()
        
        # Pre-allocate reserved slots
        self._pre_allocate_reserved_slots()
        
        # Generate initial population
        self._generate_cromosom()
        
        # Main GA loop
        while self.generataion < self.max_generataion and not self.success:
            self.generataion += 1
            
            # Calculate fitness
            self._calculate_all_fitness()
            
            # Progress callback
            if progress_callback:
                progress_callback(
                    self.generataion,
                    self.best_fitness,
                    f"Generation {self.generataion}: Best fitness {self.best_fitness:.4f}"
                )
            
            # Check for success or early termination
            if self.best_fitness >= self.early_termination:
                self.success = True
                break
            
            if not self.success:
                self._selection()
                self._crossover()
                self._mutation()
        
        self.statistics['end_time'] = perf_counter()
        self._finalize_statistics()
        
        return self._format_results()
    
    def _pre_allocate_reserved_slots(self):
        """Pre-allocate reserved slots"""
        self.reserved_schedule = {}
        
        for dosen, prefs in self.preferensi_dosen_enhanced.items():
            for slot in prefs.get('reserved_slots', []):
                waktu_idx = slot['waktu']
                ruang_idx = slot.get('ruang', 'any')
                
                if ruang_idx == 'any':
                    key = f"waktu_{waktu_idx}_any"
                else:
                    key = f"waktu_{waktu_idx}_ruang_{ruang_idx}"
                
                self.reserved_schedule[key] = {
                    'dosen': dosen,
                    'priority': slot['priority'],
                    'reason': slot.get('reason', 'Reserved slot')
                }
    
    def _generate_cromosom(self):
        """Generate initial chromosome population"""
        for i in range(self.jml_kromosom):
            self.crommosom[i] = {
                index: {
                    'kuliah': index,
                    'ruang': random.randint(0, len(self.ruangan)-1),
                    'waktu': random.randint(0, len(self.waktu)-1)
                } for index in range(len(self.kuliah))
            }
    
    def _calculate_all_fitness(self):
        """Calculate fitness for all chromosomes"""
        for i in range(len(self.crommosom)):
            self._calculate_fitness(i)
    
    def _calculate_fitness(self, cro_idx: int):
        """Calculate fitness for a single chromosome"""
        kromosom_data = self.crommosom[cro_idx]
        
        # Count clashes
        cd_clashes = self._check_clash_dosen(kromosom_data)
        cr_clashes = self._check_clash_ruangan(kromosom_data)
        cd = len(cd_clashes)
        cr = len(cr_clashes)
        
        # Calculate penalties
        total_penalties = (cd + cr) * self.config.get('constraints', {}).get('clashWeight', 100)
        
        # Enhanced constraints (simplified for demo)
        reserved_violations = []
        preference_violations = []
        
        # Check basic preferences
        for gene_idx, gene in kromosom_data.items():
            kuliah_dosen = self.kuliah[gene['kuliah']]['dosen']
            waktu_idx = gene['waktu']
            
            if kuliah_dosen in self.preferensi_dosen:
                prefs = self.preferensi_dosen[kuliah_dosen]
                
                # Check blocked times
                if waktu_idx in prefs.get('tidak_bisa_waktu', []):
                    preference_violations.append({
                        'gen_idx': gene_idx,
                        'violation_type': 'blocked_slot',
                        'penalty_weight': self.preference_weights['blocked']
                    })
                    total_penalties += self.preference_weights['blocked']
                
                # Check if not in preferred times
                elif waktu_idx not in prefs.get('preferensi_waktu', []):
                    preference_violations.append({
                        'gen_idx': gene_idx,
                        'violation_type': 'not_preferred',
                        'penalty_weight': self.preference_weights['preferred']
                    })
                    total_penalties += self.preference_weights['preferred']
        
        # Calculate fitness
        fitness_value = 1 / (1 + total_penalties)
        
        # Store fitness information
        self.fitness[cro_idx] = {
            'nilai': fitness_value,
            'total_penalties': total_penalties,
            'clash': {'cd': cd_clashes, 'cr': cr_clashes},
            'reserved_violations': reserved_violations,
            'preference_violations': preference_violations,
            'all_clash': list(set(list(cd_clashes.keys()) + list(cr_clashes.keys())))
        }
        
        # Update best fitness
        if fitness_value > self.best_fitness:
            self.best_fitness = fitness_value
            self.best_cromosom = cro_idx
        
        # Check success criteria
        if len(reserved_violations) == 0 and cd == 0 and cr == 0:
            self.success = True
    
    def _check_clash_dosen(self, kromosom_data: Dict) -> Dict:
        """Check for lecturer clashes"""
        result = {}
        for i in range(len(kromosom_data)-1):
            for j in range(i+1, len(kromosom_data)):
                dosen1 = self.kuliah[kromosom_data[i]['kuliah']]['dosen']
                dosen2 = self.kuliah[kromosom_data[j]['kuliah']]['dosen']
                
                if dosen1 == dosen2:
                    if self._is_time_clash(kromosom_data[i], kromosom_data[j]):
                        result[i] = i
                        result[j] = j
        return result
    
    def _check_clash_ruangan(self, kromosom_data: Dict) -> Dict:
        """Check for room clashes"""
        result = {}
        for i in range(len(kromosom_data)-1):
            for j in range(i+1, len(kromosom_data)):
                if self.ruangan[kromosom_data[i]['ruang']][1] == self.ruangan[kromosom_data[j]['ruang']][1]:
                    if self._is_time_clash(kromosom_data[i], kromosom_data[j]):
                        result[i] = i
                        result[j] = j
        return result
    
    def _is_time_clash(self, gen1: Dict, gen2: Dict) -> bool:
        """Check if two genes have time clash"""
        # Simplified time clash check
        if gen1['waktu'] == gen2['waktu']:
            return True
        
        # Check same day overlap (simplified)
        waktu1 = self.waktu[gen1['waktu']]
        waktu2 = self.waktu[gen2['waktu']]
        
        if waktu1[1] == waktu2[1]:  # Same day
            # For simplicity, assume no overlap if different time slots
            # In real implementation, you'd check actual time overlap
            return False
        
        return False
    
    def _selection(self):
        """Roulette wheel selection"""
        # Calculate total fitness
        total_fitness = sum(fit['nilai'] for fit in self.fitness if fit)
        if total_fitness == 0:
            return
        
        # Calculate probabilities
        probabilities = [fit['nilai'] / total_fitness for fit in self.fitness]
        
        # Select new population
        new_population = []
        for _ in range(self.jml_kromosom):
            selected = self._roulette_selection(probabilities)
            new_population.append(self.crommosom[selected].copy())
        
        self.crommosom = new_population
    
    def _roulette_selection(self, probabilities: List[float]) -> int:
        """Roulette wheel selection"""
        r = random.random()
        cumulative = 0
        for i, prob in enumerate(probabilities):
            cumulative += prob
            if r <= cumulative:
                return i
        return len(probabilities) - 1
    
    def _crossover(self):
        """Single-point crossover"""
        crossover_prob = self.crossover_rate / 100
        parents = []
        
        # Select parents
        for i in range(self.jml_kromosom):
            if random.random() <= crossover_prob:
                parents.append(i)
        
        if len(parents) < 2:
            return
        
        # Perform crossover
        for i in range(0, len(parents) - 1, 2):
            parent1 = self.crommosom[parents[i]]
            parent2 = self.crommosom[parents[i + 1]]
            
            # Single-point crossover
            crossover_point = random.randint(1, len(parent1) - 1)
            
            # Create offspring
            offspring1 = {}
            offspring2 = {}
            
            for j in range(len(parent1)):
                if j < crossover_point:
                    offspring1[j] = parent1[j].copy()
                    offspring2[j] = parent2[j].copy()
                else:
                    offspring1[j] = parent2[j].copy()
                    offspring2[j] = parent1[j].copy()
            
            self.crommosom[parents[i]] = offspring1
            self.crommosom[parents[i + 1]] = offspring2
    
    def _mutation(self):
        """Mutation operation"""
        mutation_prob = self.mutation_rate / 100
        total_genes = self.jml_kromosom * len(self.kuliah)
        num_mutations = int(mutation_prob * total_genes)
        
        for _ in range(num_mutations):
            # Select random chromosome and gene
            cro_idx = random.randint(0, self.jml_kromosom - 1)
            gene_idx = random.randint(0, len(self.kuliah) - 1)
            
            # Mutate
            self.crommosom[cro_idx][gene_idx]['waktu'] = random.randint(0, len(self.waktu) - 1)
            self.crommosom[cro_idx][gene_idx]['ruang'] = random.randint(0, len(self.ruangan) - 1)
    
    def _finalize_statistics(self):
        """Finalize statistics after optimization"""
        self.statistics.update({
            'execution_time': self.statistics['end_time'] - self.statistics['start_time'],
            'generations_completed': self.generataion,
            'best_fitness': self.best_fitness,
            'success_achieved': self.success,
            'ram_usage_mb': int(psutil.virtual_memory().used / 1024 / 1024)
        })
        
        # Count violations from best chromosome
        if self.best_cromosom < len(self.fitness) and self.fitness[self.best_cromosom]:
            best_fitness_data = self.fitness[self.best_cromosom]
            self.statistics.update({
                'total_violations': len(best_fitness_data.get('all_clash', [])),
                'reserved_violations': len(best_fitness_data.get('reserved_violations', [])),
                'preference_violations': len(best_fitness_data.get('preference_violations', [])),
                'clashes': len(best_fitness_data.get('clash', {}).get('cd', {})) + len(best_fitness_data.get('clash', {}).get('cr', {}))
            })
    
    def _format_results(self) -> Dict[str, Any]:
        """Format results for web interface"""
        best_schedule = self.crommosom[self.best_cromosom] if self.best_cromosom < len(self.crommosom) else {}
        
        # Get violations information
        violations = {}
        if self.best_cromosom < len(self.fitness) and self.fitness[self.best_cromosom]:
            fitness_data = self.fitness[self.best_cromosom]
            violations = {
                'reserved_violations': [v['gen_idx'] for v in fitness_data.get('reserved_violations', [])],
                'preference_violations': [v['gen_idx'] for v in fitness_data.get('preference_violations', [])],
                'clashes': fitness_data.get('all_clash', [])
            }
        
        return {
            'best_schedule': best_schedule,
            'statistics': self.statistics,
            'violations': violations,
            'success': self.success,
            'configuration': self.config
        }