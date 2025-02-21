import numpy as np

def maxroll_curve(value, factor):
    return value / (value + factor)

def calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit, trials=100000):
    # Compute effective multipliers using maxroll returns
    effective_sdb = maxroll_curve(sdb, 3000)
    effective_crit = maxroll_curve(crit, 6000)
    effective_hac = maxroll_curve(hac, 1000)
    
    # Compute skill damage range
    min_skill_damage = (base_min_damage * 6.1) + 232
    max_skill_damage = (base_max_damage * 6.1) + 232
    
    # Compute healing range
    min_heal = min_skill_damage * (1 + effective_sdb) * (1 + skill_heal)
    max_heal = max_skill_damage * (1 + effective_sdb) * (1 + skill_heal)
    
    # Compute probabilities
    crit_prob = effective_crit
    hac_prob = effective_hac
    
    # Monte Carlo Simulation
    heal_values = []
    crit_count = 0
    hac_count = 0
    crit_hac_count = 0
    
    for _ in range(trials):
        heal = np.random.uniform(min_heal, max_heal)
        is_crit = np.random.rand() < crit_prob
        is_hac = np.random.rand() < hac_prob
        
        if is_crit:
            heal = max_heal  # Crit ensures max heal
            crit_count += 1
        if is_hac:
            heal *= 2  # Heavy Attack doubles heal
            hac_count += 1
        if is_crit and is_hac:
            crit_hac_count += 1
        
        heal_values.append(heal)
    
    return {
        "avg_heal": np.mean(heal_values),
        "min_heal": min_heal,
        "max_heal": max_heal,
        "percentiles": np.percentile(heal_values, [5, 50, 95]),
        "sdb_maxroll": effective_sdb,
        "crit_maxroll": effective_crit,
        "hac_maxroll": effective_hac,
        "crit_percentage": (crit_count / trials) * 100,
        "hac_percentage": (hac_count / trials) * 100,
        "crit_hac_percentage": (crit_hac_count / trials) * 100
    }

def compare_runes(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit):
    results = {}
    
    # Base Case (No Rune)
    results["Base"] = calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit)
    
    # Adding Runes
    results["+30 Skill Damage Boost"] = calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb + 30, hac, crit)
    results["+30 Heavy Attack Chance"] = calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac + 30, crit)
    results["+30 Crit Chance"] = calculate_heal(base_min_damage, base_max_damage, skill_heal, sdb, hac, crit + 30)
    results["+3% Skill Heal (Chaos Rune)"] = calculate_heal(base_min_damage, base_max_damage, skill_heal + 0.03, sdb, hac, crit)
    
    # Print results
    for rune, data in results.items():
        print(f"{rune}: Average Heal = {data['avg_heal']:.2f}")
        print(f"    Min Heal: {data['min_heal']:.2f}")
        print(f"    Max Heal: {data['max_heal']:.2f}")
        print(f"    SDB Maxroll: {data['sdb_maxroll']:.4f}")
        print(f"    Crit Maxroll: {data['crit_maxroll']:.4f}")
        print(f"    HAC Maxroll: {data['hac_maxroll']:.4f}")
        print(f"    Crit Chance %: {data['crit_percentage']:.2f}")
        print(f"    HAC Chance %: {data['hac_percentage']:.2f}")
        print(f"    Crit + HAC Chance %: {data['crit_hac_percentage']:.2f}")
        print()
    
    return results

# Example usage
compare_runes(base_min_damage=157, base_max_damage=306, skill_heal=0.5591, sdb=460, hac=600, crit=630)
