#!/usr/bin/env python3

import math
from typing import Dict, List, Any, Tuple

class ParameterOptimizer:
    """
    Automatically determine optimal genetic algorithm parameters
    based on data characteristics and problem complexity
    """
    
    def __init__(self, data: Dict[str, List]):
        """
        Initialize with schedule data
        
        Args:
            data: Dictionary containing kuliah, dosen, waktu, ruangan, preferences
        """
        self.data = data
        self.kuliah = data.get('kuliah', [])
        self.dosen = data.get('dosen', [])
        self.waktu = data.get('waktu', [])
        self.ruangan = data.get('ruangan', [])
        self.preferences = data.get('preferences', [])
        
    def analyze_problem_complexity(self) -> Dict[str, Any]:
        """
        Analyze the complexity of the scheduling problem
        
        Returns:
            Dictionary with complexity metrics
        """
        n_kuliah = len(self.kuliah)
        n_dosen = len(self.dosen)
        n_waktu = len(self.waktu)
        n_ruangan = len(self.ruangan)
        n_preferences = len(self.preferences)
        
        # Calculate search space size (rough estimate)
        search_space_size = (n_waktu * n_ruangan) ** n_kuliah
        
        # Calculate constraint density
        total_possible_assignments = n_kuliah * n_waktu * n_ruangan
        constraint_density = n_preferences / max(total_possible_assignments, 1)
        
        # Calculate dosen load distribution
        dosen_loads = {}
        for kuliah in self.kuliah:
            dosen = kuliah.get('nama_dosen', 'Unknown')
            if dosen in dosen_loads:
                dosen_loads[dosen] += 1
            else:
                dosen_loads[dosen] = 1
        
        avg_dosen_load = sum(dosen_loads.values()) / max(len(dosen_loads), 1)
        max_dosen_load = max(dosen_loads.values()) if dosen_loads else 0
        load_variance = sum((load - avg_dosen_load) ** 2 for load in dosen_loads.values()) / max(len(dosen_loads), 1)
        
        # Calculate time utilization
        time_utilization = n_kuliah / max(n_waktu, 1)
        room_utilization = n_kuliah / max(n_ruangan, 1)
        
        # Complexity score (0-1, where 1 is most complex)
        complexity_factors = [
            min(math.log10(max(search_space_size, 1)) / 20, 1.0),  # Search space complexity
            min(constraint_density * 10, 1.0),  # Constraint complexity
            min(load_variance / 10, 1.0),  # Load distribution complexity
            min(time_utilization / 2, 1.0),  # Time pressure
            min(room_utilization / 2, 1.0)   # Resource pressure
        ]
        
        overall_complexity = sum(complexity_factors) / len(complexity_factors)
        
        return {
            'n_kuliah': n_kuliah,
            'n_dosen': n_dosen,
            'n_waktu': n_waktu,
            'n_ruangan': n_ruangan,
            'n_preferences': n_preferences,
            'search_space_size': search_space_size,
            'constraint_density': constraint_density,
            'avg_dosen_load': avg_dosen_load,
            'max_dosen_load': max_dosen_load,
            'load_variance': load_variance,
            'time_utilization': time_utilization,
            'room_utilization': room_utilization,
            'overall_complexity': overall_complexity,
            'complexity_level': self._get_complexity_level(overall_complexity)
        }
    
    def _get_complexity_level(self, complexity: float) -> str:
        """Convert complexity score to human-readable level"""
        if complexity < 0.3:
            return 'Low'
        elif complexity < 0.6:
            return 'Medium'
        elif complexity < 0.8:
            return 'High'
        else:
            return 'Very High'
    
    def calculate_optimal_parameters(self) -> Dict[str, Any]:
        """
        Calculate optimal GA parameters based on problem characteristics
        
        Returns:
            Dictionary with recommended parameters and explanations
        """
        analysis = self.analyze_problem_complexity()
        
        n_kuliah = analysis['n_kuliah']
        complexity = analysis['overall_complexity']
        constraint_density = analysis['constraint_density']
        
        # Population Size Calculation
        # Base: 4-20, scale with problem size and complexity
        base_pop_size = max(8, min(20, math.ceil(math.sqrt(n_kuliah))))
        complexity_multiplier = 1 + (complexity * 0.5)  # 1.0 to 1.5x
        population_size = max(4, min(20, int(base_pop_size * complexity_multiplier)))
        
        # Max Generations Calculation  
        # Base: 50-500, scale with complexity and convergence difficulty
        if complexity < 0.3:
            max_generations = max(20, min(100, n_kuliah * 2))
        elif complexity < 0.6:
            max_generations = max(50, min(200, n_kuliah * 3))
        elif complexity < 0.8:
            max_generations = max(100, min(300, n_kuliah * 4))
        else:
            max_generations = max(150, min(500, n_kuliah * 5))
        
        # Crossover Rate Calculation
        # Higher complexity -> lower crossover rate (more exploration)
        if complexity < 0.4:
            crossover_rate = 0.8  # High exploitation
        elif complexity < 0.7:
            crossover_rate = 0.75  # Balanced
        else:
            crossover_rate = 0.65  # More exploration
            
        # Mutation Rate Calculation
        # Higher complexity/constraints -> higher mutation rate
        base_mutation = 0.1
        constraint_factor = min(constraint_density * 0.2, 0.15)  # 0 to 0.15
        complexity_factor = complexity * 0.1  # 0 to 0.1
        mutation_rate = min(0.4, base_mutation + constraint_factor + complexity_factor)
        
        # Performance predictions
        estimated_time = self._estimate_execution_time(
            population_size, max_generations, n_kuliah
        )
        
        convergence_probability = self._estimate_convergence_probability(
            population_size, max_generations, complexity
        )
        
        return {
            'parameters': {
                'population_size': population_size,
                'max_generations': max_generations,
                'crossover_rate': round(crossover_rate, 2),
                'mutation_rate': round(mutation_rate, 3)
            },
            'analysis': analysis,
            'recommendations': {
                'estimated_time_seconds': estimated_time,
                'convergence_probability': convergence_probability,
                'explanation': self._generate_explanation(analysis, {
                    'population_size': population_size,
                    'max_generations': max_generations,
                    'crossover_rate': crossover_rate,
                    'mutation_rate': mutation_rate
                })
            }
        }
    
    def _estimate_execution_time(self, pop_size: int, max_gen: int, n_kuliah: int) -> float:
        """Estimate execution time in seconds"""
        # Base time per generation per chromosome (empirical)
        base_time_per_gen = 0.01  # seconds
        kuliah_factor = math.log10(max(n_kuliah, 1)) / 3  # Scale with problem size
        
        estimated_time = pop_size * max_gen * base_time_per_gen * (1 + kuliah_factor)
        return round(estimated_time, 1)
    
    def _estimate_convergence_probability(self, pop_size: int, max_gen: int, complexity: float) -> float:
        """Estimate probability of finding good solution"""
        # Factors that increase convergence probability
        size_factor = min(pop_size / 10, 1.0)  # Larger population helps
        generation_factor = min(max_gen / 100, 1.0)  # More generations help
        
        # Complexity reduces convergence probability
        complexity_penalty = complexity * 0.3
        
        base_probability = 0.7
        probability = base_probability + (size_factor * 0.2) + (generation_factor * 0.1) - complexity_penalty
        
        return max(0.1, min(0.95, round(probability, 2)))
    
    def _generate_explanation(self, analysis: Dict, parameters: Dict) -> Dict[str, str]:
        """Generate human-readable explanations for parameter choices"""
        explanations = {}
        
        # Population size explanation
        if parameters['population_size'] <= 8:
            explanations['population_size'] = f"Small population ({parameters['population_size']}) for {analysis['complexity_level'].lower()} complexity problem - faster convergence"
        elif parameters['population_size'] <= 12:
            explanations['population_size'] = f"Medium population ({parameters['population_size']}) balances exploration and speed"
        else:
            explanations['population_size'] = f"Large population ({parameters['population_size']}) for complex problem - better exploration"
        
        # Generation explanation
        if parameters['max_generations'] <= 100:
            explanations['max_generations'] = f"Moderate generations ({parameters['max_generations']}) - problem should converge quickly"
        elif parameters['max_generations'] <= 200:
            explanations['max_generations'] = f"Extended generations ({parameters['max_generations']}) for thorough search"
        else:
            explanations['max_generations'] = f"Many generations ({parameters['max_generations']}) - complex problem needs extensive search"
        
        # Crossover explanation
        if parameters['crossover_rate'] >= 0.75:
            explanations['crossover_rate'] = f"High crossover rate ({parameters['crossover_rate']}) - exploit good solutions"
        else:
            explanations['crossover_rate'] = f"Moderate crossover rate ({parameters['crossover_rate']}) - balance exploration/exploitation"
        
        # Mutation explanation
        if parameters['mutation_rate'] <= 0.1:
            explanations['mutation_rate'] = f"Low mutation rate ({parameters['mutation_rate']}) - stable convergence"
        elif parameters['mutation_rate'] <= 0.2:
            explanations['mutation_rate'] = f"Medium mutation rate ({parameters['mutation_rate']}) - good diversity"
        else:
            explanations['mutation_rate'] = f"High mutation rate ({parameters['mutation_rate']}) - escape local optima"
        
        return explanations
    
    def get_parameter_recommendations(self) -> Dict[str, Any]:
        """
        Get parameter recommendations with multiple options
        
        Returns:
            Dictionary with conservative, balanced, and aggressive parameter sets
        """
        optimal = self.calculate_optimal_parameters()
        analysis = optimal['analysis']
        base_params = optimal['parameters']
        
        # Conservative (faster, less thorough)
        conservative = {
            'population_size': max(4, base_params['population_size'] - 2),
            'max_generations': max(20, int(base_params['max_generations'] * 0.7)),
            'crossover_rate': min(0.9, base_params['crossover_rate'] + 0.1),
            'mutation_rate': max(0.05, base_params['mutation_rate'] - 0.05)
        }
        
        # Aggressive (slower, more thorough)
        aggressive = {
            'population_size': min(20, base_params['population_size'] + 3),
            'max_generations': min(500, int(base_params['max_generations'] * 1.5)),
            'crossover_rate': max(0.5, base_params['crossover_rate'] - 0.1),
            'mutation_rate': min(0.4, base_params['mutation_rate'] + 0.1)
        }
        
        return {
            'analysis': analysis,
            'recommendations': {
                'conservative': {
                    'parameters': conservative,
                    'description': 'Fast execution, good for simple problems',
                    'estimated_time': self._estimate_execution_time(
                        conservative['population_size'], 
                        conservative['max_generations'], 
                        analysis['n_kuliah']
                    )
                },
                'balanced': {
                    'parameters': base_params,
                    'description': 'Optimal balance of speed and quality',
                    'estimated_time': optimal['recommendations']['estimated_time_seconds']
                },
                'aggressive': {
                    'parameters': aggressive,
                    'description': 'Thorough search, best for complex problems',
                    'estimated_time': self._estimate_execution_time(
                        aggressive['population_size'], 
                        aggressive['max_generations'], 
                        analysis['n_kuliah']
                    )
                }
            },
            'optimal_choice': 'balanced',  # Default recommendation
            'explanations': optimal['recommendations']['explanation']
        }