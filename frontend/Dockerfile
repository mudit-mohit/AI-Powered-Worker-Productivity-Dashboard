# Production stage
FROM node:18-alpine

WORKDIR /app

# Install serve to run the production build
RUN npm install -g serve

# Copy pre-built app from local build folder
COPY build ./build

# Expose port
EXPOSE 3000

# Set environment variable
ENV NODE_ENV=production

# Run the application
CMD ["serve", "-s", "build", "-l", "3000"]
