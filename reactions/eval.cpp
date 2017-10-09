#include "../../bbcache/src/evaluate.hh"
#include <unistd.h>

#define BUFSZ  1024

int exists(const char *file)
{
	FILE *fp = NULL;
	if(fp = fopen(file, "r")) {
		fclose(fp);
		//printf("%s exists\n", file);
		return 1;
	}

	//printf("%s doesn't exist\n", file);

	return 0;
}

int main(int argc, char **argv)
{
	double c = 0.01;
	const char *out_file = "data/train.out";

	VECTOR total_captured_correct;
	int ntotal_captured_correct = 0;
	int nsamples = 120;

	rule_vinit(nsamples, &total_captured_correct);
	make_default(&total_captured_correct, nsamples);

	char model_file[BUFSZ], label_file[BUFSZ];

	int num_bits = 881;
	double thres = 0.85;

	for(int i = 0; i < num_bits; i++) {
		sprintf(model_file, "data/train/p1_bit%d.opt", i);
		sprintf(label_file, "data/train/p1_bit%d.label", i);

		if(!exists(model_file) || !exists(label_file)) {
			//printf("continue");
			continue;
		}
		//printf("not continue (%d)\n", i);

		VECTOR captured_correct;

		rule_vinit(nsamples, &captured_correct);

		//printf("%s   %s\n", model_file, label_file);

		double a = 1.0;

		if(evaluate(model_file, out_file, label_file, &captured_correct, c, 1) != -1.0) {
			a = (double)count_ones_vector(captured_correct, nsamples) / (double)nsamples;

			//if(a > 0.0) {
				rule_vand(total_captured_correct, total_captured_correct, captured_correct, nsamples, &ntotal_captured_correct);

				if(a < thres) {
					printf("%s accuracy: %f\n", model_file, a);
				}
			//}
		}

		//printf("%ld\n", mpz_popcount(captured_correct));


		rule_vfree(&captured_correct);
	}

	printf("Final accuracy: %f\n", (double)ntotal_captured_correct / (double)nsamples);

	rule_vfree(&total_captured_correct);

	return 0;
}
