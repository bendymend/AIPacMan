
 (load "~/quicklisp/setup.lisp")
(ql:quickload "cl-csv")
(defparameter data (cl-csv:read-csv #P"stats_new.csv"))
(defparameter minimax_list ())
(defparameter time_strings ())
(defparameter time_numbers ())
(defparameter points_strings ())
(defparameter points_numbers ())
(defparameter exp_value_time 0)
(defparameter mean_points 0)
(defparameter variance_points 0)

(loop for a in data
   do (if (string-equal (NTH 0 a) "MinimaxAgent")
             (push a minimax_list)))

(loop for a in minimax_list
   do (push (String-left-trim "0:00:" (NTH 2 a)) time_strings))

(loop for a in minimax_list
   do (push (NTH 3 a) points_strings))

(loop for a in time_strings
   do (push (NTH 0 (with-input-from-string (in a)
  (loop for x = (read in nil nil) while x collect x))) time_numbers))

(loop for a in points_strings
   do (push (NTH 0 (with-input-from-string (in a)
  (loop for x = (read in nil nil) while x collect x))) points_numbers))

(setq exp_value_time (/ (apply '+ time_numbers) (length time_numbers)))

(setq mean_points (/ (apply '+ points_numbers) (length points_numbers)))

(setq variance_points (/ (apply '+ (mapcar (lambda (x) (* x x)) (mapcar (lambda (n) (- n mean_points))
        points_numbers))) (length points_numbers)))

exp_value_time
variance_points