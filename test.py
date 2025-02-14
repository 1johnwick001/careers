# {% if messages %}
#     {% for message in messages %}
#     <div class="alert alert-{{ message.tags }}">
#         {{ message }}
#     </div>
#     {% endfor %}
# {% endif %}


#  <form method="post" action="{% url 'accounts:login_page' %}">
#                             {% csrf_token %}
                            
#                             <div class="ezy__signin16-form-card">
#                                 <!-- Username Field -->
#                                 <div class="form-group w-100 mb-3">
#                                     <input 
#                                         type="text" 
#                                         class="form-control {% if form.username.errors %}is-invalid{% endif %}" 
#                                         name="username" 
#                                         placeholder="Username"
#                                         value="{{ form.username.value|default:'' }}"
#                                         required
#                                     >
#                                     {% if form.username.errors %}
#                                         <div class="error-message">
#                                             {{ form.username.errors }}
#                                         </div>
#                                     {% endif %}
#                                 </div>

#                                 <!-- Password Field -->
#                                 <div class="form-group w-100 mb-3">
#                                     <input 
#                                         type="password" 
#                                         class="form-control {% if form.password.errors %}is-invalid{% endif %}" 
#                                         name="password" 
#                                         placeholder="Password"
#                                         required
#                                     >
#                                     {% if form.password.errors %}
#                                         <div class="error-message">
#                                             {{ form.password.errors }}
#                                         </div>
#                                     {% endif %}
#                                 </div>

#                                 <!-- Login Button -->
#                                 <button type="submit" class="btn ezy__signin16-btn w-100">
#                                     SIGN IN
#                                 </button>
#                             </div>

#                             <!-- Forgot Password and Register Links -->
#                             <div class="text-center mt-4">
#                                 {% comment %} <a href="{% url 'accounts:password_reset' %}" class="me-3">Forgot Password?</a> {% endcomment %}
#                                 <a href="{% url 'accounts:register_page' %}">Don't have an account?</a>
#                             </div>
#                         </form>

# <style>
#         .error-message {
#             color: #dc3545;
#             font-size: 0.875rem;
#             margin-top: 0.25rem;
#         }

#         .alert-danger {
#             background-color: #f8d7da;
#             color: #721c24;
#             padding: 10px;
#             border-radius: 4px;
#             margin-bottom: 15px;
#         }
#     </style>