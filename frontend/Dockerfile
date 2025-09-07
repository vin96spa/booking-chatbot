# Use Node 20 for Vite 5 compatibility
FROM node:20-alpine

# Install necessary build tools
RUN apk add --no-cache python3 make g++

WORKDIR /usr/src/app

# Copy package files
COPY package*.json ./

# Clean install with proper cleanup
RUN rm -rf node_modules package-lock.json .npm && \
    npm cache clean --force && \
    npm install --verbose --legacy-peer-deps && \
    npm rebuild

# Copy application code
COPY . .

# Expose Vite port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]