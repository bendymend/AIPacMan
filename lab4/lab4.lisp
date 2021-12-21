(require "cl-csv")
(setq elems (cl-csv:read-csv #P"stats.csv"))
(setq header (NTH 0 elems))
(setq expectimax_list ())
(setq expectimax_test_list ())
(setq expectimax_train_list ())
(setq alphabeta_list ())
(setq alphabeta_test_list ())
(setq alphabeta_train_list ())

(defun nshuffle (sequence)
  (loop for i from (length sequence) downto 2
        do (rotatef (elt sequence (random i))
                    (elt sequence (1- i))))
  sequence)

(loop for a in elems
   do (if (string-equal (NTH 0 a) "ExpectimaxAgent")
             (push a expectimax_list)))
(loop for a in elems
   do (if (string-equal (NTH 0 a) "AlphaBetaAgent")
             (push a alphabeta_list)))

(nshuffle expectimax_list)
(nshuffle alphabeta_list)

(setq expectimax_list_length (length expectimax_list))
(setq alphabeta_list_length (length alphabeta_list))

(loop for a from 0 to (/ (- expectimax_list_length 1) 4)
   do (push (NTH a expectimax_list) expectimax_test_list)
)

(loop for a from (+ (/ (- expectimax_list_length 1) 4) 1) to (- expectimax_list_length 1)
   do (push (NTH a expectimax_list) expectimax_train_list)
)

(loop for a from 0 to (/ (- alphabeta_list_length 1) 4)
   do (push (NTH a alphabeta_list) alphabeta_test_list)
)

(loop for a from (+ (/ (- alphabeta_list_length 1) 4) 1) to (- alphabeta_list_length 1)
   do (push (NTH a alphabeta_list) alphabeta_train_list)
)

(push header alphabeta_train_list)
(push header alphabeta_test_list)
(push header expectimax_train_list)
(push header expectimax_test_list)

(with-open-file (stream "stats_expectimax_test.csv"
                     :direction :output
                     :if-exists :supersede
                     :if-does-not-exist :create)
                     (cl-csv:write-csv expectimax_test_list :stream stream))

(with-open-file (stream "stats_expectimax_train.csv"
                     :direction :output
                     :if-exists :supersede
                     :if-does-not-exist :create)
                     (cl-csv:write-csv expectimax_train_list :stream stream))

(with-open-file (stream "stats_alphabeta_train.csv"
                     :direction :output
                     :if-exists :supersede
                     :if-does-not-exist :create)
                     (cl-csv:write-csv alphabeta_train_list :stream stream))

(with-open-file (stream "stats_alphabeta_test.csv"
                     :direction :output
                     :if-exists :supersede
                     :if-does-not-exist :create)
                     (cl-csv:write-csv alphabeta_test_list :stream stream))
