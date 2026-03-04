# Using super light Nginx
FROM nginx:alpine

# Delete default configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our configuration
COPY nginx.conf /etc/nginx/conf.d/

# Copy our web files
COPY index.html /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]