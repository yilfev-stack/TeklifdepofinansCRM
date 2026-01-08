FROM node:18-alpine

WORKDIR /app

COPY package.json ./

# Clean install with legacy peer deps and force ajv resolution
RUN npm install --legacy-peer-deps && \
    npm install ajv@8 --save-dev --legacy-peer-deps

COPY . .

ENV REACT_APP_BACKEND_URL=http://localhost:8001

EXPOSE 3000

CMD ["npm", "start"]
