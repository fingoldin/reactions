#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#include <gmp.h>

#include "rule.h"

typedef enum gate_en {
    G_AND = 0,
    G_IOR,
    G_XOR,
    G_COUNT
} GATE;

const char *gate_names[] = {"&", "|", "!|"};

int generate_rule(rule_t *dest, rule_t src1, rule_t src2, GATE gate, int nsamples, double min_support, int no_repeat)
{
    mpz_init2(dest->truthtable, nsamples);

    switch(gate)
    {
        case G_AND:
            mpz_and(dest->truthtable, src1.truthtable, src2.truthtable);
            break;
        case G_IOR:
            mpz_ior(dest->truthtable, src1.truthtable, src2.truthtable);
            break;
        case G_XOR:
            mpz_xor(dest->truthtable, src1.truthtable, src2.truthtable);
            break;
        default:
            break;
    };

    int support = mpz_popcount(dest->truthtable);
    if((double)support / (double)nsamples < min_support) {
        mpz_clear(dest->truthtable);
        return 1;
    }

    if(no_repeat) {
        dest->containslen = src1.containslen + src2.containslen;
        dest->contains = malloc(sizeof(int) * dest->containslen);
        memcpy(dest->contains, src1.contains, sizeof(int) * src1.containslen);
        memcpy(dest->contains + src1.containslen, src2.contains, sizeof(int) * src2.containslen);
    }

    dest->support = support;

    int len1 = strlen(src1.features);
    int len2 = strlen(src2.features);
    int len3 = strlen(gate_names[gate]);
    dest->features = malloc(len1 + len2 + len3 + 3);

    strcpy(dest->features, src2.features);
    strcat(dest->features, gate_names[gate]);
    strcat(dest->features, "(");
    strcat(dest->features, src1.features);
    strcat(dest->features, ")");

    //printf("%s\n", dest->features);

    return 0;
}

int main(int argc, char **argv)
{
    const char *base_out_path = "../bbcache/data/haberman_R.out";
    int max_cardinality = 5;
    GATE gates[] = {G_AND, G_IOR, G_XOR};
    int num_gates = 3;
    double min_support = 0.0;
    int no_repeat = 1;
    int log_freq = 100000;

    int nsamples;
    rule_t **rules = malloc(sizeof(rule_t*) * max_cardinality);
    int *nrules = malloc(sizeof(int) * max_cardinality);

    // contains only rules with cardinality > 1
    int **rule_contains;

    if(rules_init(base_out_path, &nrules[0], &nsamples, &rules[0], 0) != 0) {
        printf("Could not load base out file\n");
        free(rules);
        free(nrules);
        return 1;
    }

    if(no_repeat) {
        for(int i = 0; i < nrules[0]; i++) {
            rules[0][i].contains = malloc(sizeof(int));
            *(rules[0][i].contains) = i;
            rules[0][i].containslen = 1;
        }
    }

    int total_rule_idx = 0;
    // card is actually one less than the cardinality it represents
    for(int card = 1; card < max_cardinality; card++) {
        int rule_idx = 0;

        for(int rule1_idx = 0; rule1_idx < nrules[card-1]; rule1_idx++) {
            for(int rule2_idx = (card == 1 ? rule1_idx+1 : 0); rule2_idx < nrules[0]; rule2_idx++) {
                if(no_repeat) {
                    int contains = 0;
                    for(int j = 0; j < rules[card-1][rule1_idx].containslen; j++) {
                        if(rules[card-1][rule1_idx].contains[j] == rule2_idx) {
                            contains = 1;
                            break;
                        }
                    }
printf("dick");
                    if(contains)
                        continue;
                }

                for(GATE gate = 0; gate < num_gates; gate++) {
                    rule_t temp;

                    if(generate_rule(&temp, rules[card-1][rule1_idx], rules[0][rule2_idx], gates[gate], nsamples, min_support, no_repeat) == 0) {
                        rules[card] = realloc(rules[card], sizeof(rule_t) * (rule_idx + 1));
                        memcpy(&rules[card][rule_idx], &temp, sizeof(rule_t));

                        total_rule_idx++;
                        if(total_rule_idx % log_freq == 0)
                            printf("Generated %d rules\n", total_rule_idx);

                        rule_idx++;
                    }
                }
            }
        }

        nrules[card] = rule_idx;
    }

    printf("total: %d\n", total_rule_idx);

    for(int i = 1; i < max_cardinality; i++) {
        for(int j = 0; j < nrules[i]; j++) {
            mpz_clear(rules[i][j].truthtable);
            if(no_repeat)
                free(rules[i][j].contains);
            free(rules[i][j].features);
        }
        free(rules[i]);
    }

    if(no_repeat)
        for(int i = 0; i < nrules[0]; i++)
            free(rules[0][i].contains);

    rules_free(rules[0], nrules[0], 0);

    free(rules);
    free(nrules);

    return 0;
}
