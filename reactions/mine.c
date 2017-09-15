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

typedef struct contains {
    int *data;
    int len;
} contains_t;

static const char *gate_names[] = {"&", "|", "!|"};

int generate_rule(rule_t *dest, rule_t src1, rule_t src2, GATE gate, int nsamples, double min_support, int no_repeat, contains_t *dest_contains, contains_t *src1_contains, contains_t *src2_contains)
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
        dest_contains->len = src1_contains->len + src2_contains->len;
        dest_contains->data = malloc(sizeof(int) * (dest_contains->len));
        memcpy(dest_contains->data, src1_contains->data, sizeof(int) * src1_contains->len);
        memcpy(dest_contains->data + src1_contains->len, src2_contains->data, sizeof(int) * src2_contains->len);
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
    const char *base_out_path = "../../bbcache/data/haberman_R.out";
    const char *out_file_path = "data/haberman_test2.out";
    int max_cardinality = 5;
    GATE gates[] = {G_AND, G_IOR, G_XOR};
    int num_gates = 3;
    double min_support = 0.1;
    int no_repeat = 1;
    int log_freq = 100000;

    int nsamples;
    rule_t **rules = malloc(sizeof(rule_t*) * max_cardinality);
    int *nrules = malloc(sizeof(int) * max_cardinality);

    contains_t **contains = malloc(sizeof(contains_t*) * max_cardinality);

    if(rules_init(base_out_path, &nrules[0], &nsamples, &rules[0], 0) != 0) {
        printf("Could not load base out file\n");
        free(rules);
        free(nrules);
        return 1;
    }

    printf("samples: %d\n", nsamples);

    contains[0] = malloc(sizeof(contains_t) * nrules[0]);

    if(no_repeat) {
        for(int i = 0; i < nrules[0]; i++) {
            contains[0][i].data = malloc(sizeof(int));
            *(contains[0][i].data) = i;
            contains[0][i].len = 1;
        }
    }

    int total_rule_idx = 0;
    // card is actually one less than the cardinality it represents
    for(int card = 1; card < max_cardinality; card++) {
        int rule_idx = 0;

        for(int rule1_idx = 0; rule1_idx < nrules[card-1]; rule1_idx++) {
            for(int rule2_idx = (card == 1 ? rule1_idx+1 : 0); rule2_idx < nrules[0]; rule2_idx++) {
                if(no_repeat) {
                    int isin = 0;
                    for(int j = 0; j < contains[card-1][rule1_idx].len; j++) {
                        if(contains[card-1][rule1_idx].data[j] == rule2_idx) {
                            isin = 1;
                            break;
                        }
                    }

                    if(isin)
                        continue;
                }

                for(int gate = 0; gate < num_gates; gate++) {
                    rule_t temp;
                    contains_t tcont;
                    contains_t *src1_contains = NULL, *src2_contains = NULL;

                    if(no_repeat) {
                        src1_contains = &contains[card-1][rule1_idx];
                        src2_contains = &contains[0][rule2_idx];
                    }

                    if(generate_rule(&temp, rules[card-1][rule1_idx], rules[0][rule2_idx], gates[gate], nsamples, min_support, no_repeat, &tcont, src1_contains, src2_contains) == 0) {
                        rules[card] = realloc(rules[card], sizeof(rule_t) * (rule_idx + 1));
                        if(no_repeat)
                            contains[card] = realloc(contains[card], sizeof(contains_t) * (rule_idx + 1));

                        memcpy(&rules[card][rule_idx], &temp, sizeof(rule_t));
                        if(no_repeat)
                            memcpy(&contains[card][rule_idx], &tcont, sizeof(contains_t));

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

    FILE *out_file = NULL;
    if(!(out_file = fopen(out_file_path, "w")))
        printf("Could not open out file!\n");
    else {
        for(int i = 0; i < max_cardinality; i++) {
            for(int j = 0; j < nrules[i]; j++) {
                char *bits = mpz_get_str(NULL, 2, rules[i][j].truthtable);
                fprintf(out_file, "%s %s\n", rules[i][j].features, bits);
                free(bits);
            }
        }

        fclose(out_file);
    }

    for(int i = 0; i < max_cardinality; i++) {
        for(int j = 0; j < nrules[i]; j++) {
            mpz_clear(rules[i][j].truthtable);
            if(no_repeat)
                free(contains[i][j].data);
            free(rules[i][j].features);
        }
        free(rules[i]);
        if(no_repeat)
            free(contains[i]);
    }

    free(contains);
    free(rules);
    free(nrules);

    return 0;
}
